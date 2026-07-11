import os
import re
import json

vault_path = os.path.dirname(os.path.abspath(__file__))
logs_dir = os.path.join(vault_path, "Reading Logs")

# 1. Scan and parse all reading logs
logs_data = []

if os.path.exists(logs_dir):
    for root, dirs, files in os.walk(logs_dir):
        for f in files:
            if not f.endswith(".md"):
                continue
            file_path = os.path.join(root, f)
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
            
            # Extract frontmatter
            fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
            if fm_match:
                fm_text = fm_match.group(1)
                note_body = content[fm_match.end():].strip()
                
                # Parse frontmatter properties
                log_entry = {}
                for line in fm_text.splitlines():
                    if ":" in line:
                        parts = line.split(":", 1)
                        key = parts[0].strip()
                        val = parts[1].strip().strip('"').strip("'")
                        log_entry[key] = val
                
                # Verify type and required fields
                if log_entry.get("type") == "reading-log" and "date" in log_entry:
                    try:
                        pages_read = int(log_entry.get("pages_read", 0))
                    except ValueError:
                        pages_read = 0
                        
                    material = log_entry.get("material", "").replace("[[", "").replace("]]", "")
                    chapter = log_entry.get("chapter", "")
                    page_range = log_entry.get("page_range", "")
                    
                    logs_data.append({
                        "date": log_entry["date"],
                        "material": material,
                        "chapter": chapter,
                        "page_range": page_range,
                        "pages_read": pages_read,
                        "note_body": note_body
                    })

# Sort logs by date descending
logs_data.sort(key=lambda x: x["date"], reverse=True)

# 2. Generate HTML Content
html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📚 My Reading Tracker Dashboard</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        :root {
            --bg-primary: #0b0f19;
            --bg-secondary: rgba(17, 24, 39, 0.7);
            --bg-tertiary: rgba(31, 41, 55, 0.5);
            --accent: #6366f1;
            --accent-gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
            --border: rgba(255, 255, 255, 0.08);
            --shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            background-color: var(--bg-primary);
            color: var(--text-main);
            font-family: 'Plus Jakarta Sans', sans-serif;
            min-height: 100vh;
            padding: 2rem 1.5rem;
            line-height: 1.5;
            background-image: 
                radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.1) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(139, 92, 246, 0.1) 0px, transparent 50%);
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            gap: 2rem;
        }

        header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid var(--border);
            padding-bottom: 1.5rem;
        }

        h1 {
            font-family: 'Outfit', sans-serif;
            font-size: 2.25rem;
            font-weight: 700;
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        /* Filter Banner */
        .filter-banner {
            display: none;
            background: rgba(99, 102, 241, 0.15);
            border: 1px solid var(--accent);
            border-radius: 12px;
            padding: 0.75rem 1.25rem;
            align-items: center;
            justify-content: space-between;
            font-size: 0.9rem;
            animation: fadeIn 0.3s;
        }

        .clear-filter-btn {
            background: var(--accent);
            color: white;
            border: none;
            border-radius: 6px;
            padding: 0.25rem 0.75rem;
            font-size: 0.8rem;
            cursor: pointer;
            font-weight: 600;
            transition: opacity 0.2s;
        }

        .clear-filter-btn:hover {
            opacity: 0.9;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1.5rem;
        }

        .stat-card {
            background: var(--bg-secondary);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: var(--shadow);
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            position: relative;
            overflow: hidden;
            transition: transform 0.2s;
        }

        .stat-card:hover {
            transform: translateY(-4px);
        }

        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: var(--accent-gradient);
        }

        .stat-label {
            font-size: 0.875rem;
            color: var(--text-muted);
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .stat-val {
            font-family: 'Outfit', sans-serif;
            font-size: 2rem;
            font-weight: 700;
            color: #ffffff;
        }

        .card {
            background: var(--bg-secondary);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 1.75rem;
            box-shadow: var(--shadow);
        }

        .controls-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1.5rem;
            flex-wrap: wrap;
            gap: 1rem;
        }

        .controls-left {
            display: flex;
            align-items: center;
            gap: 2.5rem;
            flex-wrap: wrap;
        }

        .control-group {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        label {
            font-size: 0.875rem;
            color: var(--text-muted);
            font-weight: 600;
        }

        input[type="number"], select {
            background: var(--bg-tertiary);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text-main);
            padding: 0.5rem 0.75rem;
            font-family: inherit;
            font-size: 0.875rem;
            outline: none;
            transition: border-color 0.2s;
        }

        input[type="number"]:focus, select:focus {
            border-color: var(--accent);
        }

        input[type="number"] {
            width: 80px;
        }

        .chart-container {
            position: relative;
            width: 100%;
            margin-top: 1rem;
        }

        .tooltip {
            position: fixed;
            display: none;
            background: rgba(15, 23, 42, 0.95);
            backdrop-filter: blur(8px);
            border: 1px solid var(--border);
            color: var(--text-main);
            padding: 0.75rem 1rem;
            border-radius: 10px;
            font-size: 0.8125rem;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
            pointer-events: none;
            z-index: 9999;
            line-height: 1.5;
            white-space: pre-line;
        }

        .tooltip strong {
            color: #ffffff;
            font-family: 'Outfit', sans-serif;
            font-size: 0.875rem;
        }

        svg {
            display: block;
            width: 100%;
            height: auto;
        }

        .bar-item {
            transition: fill-opacity 0.15s;
            cursor: pointer;
        }

        .bar-item:hover {
            fill-opacity: 0.8;
        }

        /* Raw Data Table */
        .table-section {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }

        .table-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
        }

        .search-input {
            background: var(--bg-tertiary);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text-main);
            padding: 0.5rem 1rem;
            font-family: inherit;
            font-size: 0.875rem;
            outline: none;
            min-width: 250px;
        }

        .table-wrapper {
            overflow-x: auto;
            border-radius: 12px;
            border: 1px solid var(--border);
        }

        table {
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 0.875rem;
        }

        th {
            background: var(--bg-tertiary);
            color: var(--text-muted);
            font-weight: 600;
            padding: 1rem;
            border-bottom: 1px solid var(--border);
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 0.05em;
        }

        td {
            padding: 1rem;
            border-bottom: 1px solid var(--border);
            color: var(--text-main);
            vertical-align: middle;
        }

        tr:last-child td {
            border-bottom: none;
        }

        tr:hover td {
            background: rgba(255, 255, 255, 0.02);
        }

        .book-link {
            color: var(--accent);
            text-decoration: none;
            font-weight: 500;
            cursor: pointer;
        }

        .book-link:hover {
            text-decoration: underline;
        }

        .note-row {
            cursor: pointer;
        }

        .note-btn {
            background: var(--bg-tertiary);
            border: 1px solid var(--border);
            border-radius: 6px;
            color: var(--text-main);
            padding: 0.25rem 0.5rem;
            font-size: 0.75rem;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
            transition: background 0.2s;
        }

        .note-btn:hover {
            background: rgba(255, 255, 255, 0.08);
            border-color: var(--accent);
        }

        .pagination {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.875rem;
            color: var(--text-muted);
            margin-top: 0.5rem;
        }

        .page-btn {
            background: var(--bg-tertiary);
            border: 1px solid var(--border);
            border-radius: 6px;
            color: var(--text-main);
            padding: 0.375rem 0.75rem;
            cursor: pointer;
            transition: background 0.2s;
        }

        .page-btn:hover:not(:disabled) {
            background: rgba(255, 255, 255, 0.08);
        }

        .page-btn:disabled {
            opacity: 0.4;
            cursor: not-allowed;
        }

        /* Note Reader Modal */
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(7, 10, 19, 0.85);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            z-index: 10000;
            display: none;
            align-items: center;
            justify-content: center;
            padding: 1.5rem;
            animation: fadeIn 0.2s ease-out;
        }

        .modal-content {
            background: #111827;
            border: 1px solid var(--border);
            border-radius: 24px;
            width: 100%;
            max-width: 800px;
            max-height: 85vh;
            display: flex;
            flex-direction: column;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.6);
            overflow: hidden;
            animation: scaleIn 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
        }

        .modal-header {
            padding: 1.5rem 2rem;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }

        .modal-header-info {
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
        }

        .modal-book-title {
            font-family: 'Outfit', sans-serif;
            font-size: 1.25rem;
            font-weight: 700;
            color: #ffffff;
        }

        .modal-metadata {
            font-size: 0.85rem;
            color: var(--text-muted);
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }

        .close-btn {
            background: var(--bg-tertiary);
            border: 1px solid var(--border);
            border-radius: 50%;
            width: 32px;
            height: 32px;
            color: var(--text-main);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 0.9rem;
            transition: background 0.2s;
        }

        .close-btn:hover {
            background: rgba(239, 68, 68, 0.2);
            color: #ef4444;
            border-color: rgba(239, 68, 68, 0.4);
        }

        .modal-body {
            padding: 2rem;
            overflow-y: auto;
            color: #d1d5db;
            font-size: 0.975rem;
            line-height: 1.6;
        }

        /* Rendered Markdown Styling */
        .markdown-body h1, .markdown-body h2, .markdown-body h3 {
            font-family: 'Outfit', sans-serif;
            color: #ffffff;
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
            font-weight: 600;
        }
        .markdown-body h1 { font-size: 1.5rem; }
        .markdown-body h2 { font-size: 1.25rem; }
        .markdown-body h3 { font-size: 1.1rem; }
        .markdown-body p { margin-bottom: 1rem; }
        .markdown-body ul, .markdown-body ol {
            margin-bottom: 1rem;
            padding-left: 1.5rem;
        }
        .markdown-body li { margin-bottom: 0.25rem; }
        .markdown-body blockquote {
            border-left: 4px solid var(--accent);
            background: rgba(99, 102, 241, 0.05);
            padding: 0.75rem 1.25rem;
            margin-bottom: 1rem;
            border-radius: 0 8px 8px 0;
            font-style: italic;
        }
        .markdown-body pre {
            background: var(--bg-tertiary);
            padding: 1rem;
            border-radius: 8px;
            overflow-x: auto;
            border: 1px solid var(--border);
            margin-bottom: 1rem;
        }
        .markdown-body code {
            font-family: monospace;
            background: var(--bg-tertiary);
            padding: 0.125rem 0.25rem;
            border-radius: 4px;
            font-size: 0.9em;
        }
        .markdown-body pre code {
            background: transparent;
            padding: 0;
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        @keyframes scaleIn {
            from { transform: scale(0.95); opacity: 0; }
            to { transform: scale(1); opacity: 1; }
        }

        @media (max-width: 640px) {
            body {
                padding: 1rem;
            }
            header {
                flex-direction: column;
                align-items: flex-start;
                gap: 0.5rem;
            }
            .controls-row {
                flex-direction: column;
                align-items: flex-start;
                gap: 1rem;
            }
            .controls-left {
                gap: 1rem;
            }
            .modal-content {
                max-height: 90vh;
            }
            .modal-body {
                padding: 1.25rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📚 Reading Dashboard</h1>
        </header>

        <!-- Book Filter Banner -->
        <div class="filter-banner" id="filter-banner">
            <span>Filtering by book: <strong id="filter-book-name" style="color: #ffffff;">Book Title</strong></span>
            <button class="clear-filter-btn" id="clear-filter-btn">Clear Filter</button>
        </div>

        <!-- Stats Overview -->
        <div class="stats-grid">
            <div class="stat-card">
                <span class="stat-label">Total Pages Read</span>
                <span class="stat-val" id="stat-total">0</span>
            </div>
            <div class="stat-card">
                <span class="stat-label">Daily Average</span>
                <span class="stat-val" id="stat-avg">0</span>
            </div>
            <div class="stat-card">
                <span class="stat-label">Books Read</span>
                <span class="stat-val" id="stat-books">0</span>
            </div>
            <div class="stat-card">
                <span class="stat-label">Current Streak</span>
                <span class="stat-val" id="stat-streak">0</span>
            </div>
        </div>

        <!-- Chart Card -->
        <div class="card">
            <div class="controls-row">
                <div class="controls-left">
                    <div class="control-group">
                        <label for="lookback">Look back:</label>
                        <input type="number" id="lookback" value="30" min="1">
                        <span style="font-size: 0.875rem; color: var(--text-muted);">days</span>
                    </div>
                    <div class="control-group">
                        <label for="groupby">Group by:</label>
                        <select id="groupby">
                            <option value="day">Day</option>
                            <option value="week">Week</option>
                            <option value="month">Month</option>
                            <option value="year">Year</option>
                        </select>
                    </div>
                </div>
            </div>

            <div class="chart-container" id="chart-div">
                <!-- SVG injected dynamically -->
            </div>
        </div>

        <!-- Logs Table Card -->
        <div class="card table-section">
            <div class="table-header">
                <h2 style="font-family: 'Outfit', sans-serif; font-size: 1.25rem;">📝 All Reading Logs</h2>
                <input type="text" class="search-input" id="search-box" placeholder="Search books, chapters...">
            </div>
            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Reading Material</th>
                            <th>Chapter/Section</th>
                            <th>Page Range</th>
                            <th>Pages Read</th>
                            <th style="width: 100px; text-align: center;">Notes</th>
                        </tr>
                    </thead>
                    <tbody id="table-body">
                        <!-- Table rows injected dynamically -->
                    </tbody>
                </table>
            </div>
            <div class="pagination">
                <span id="page-indicator">Showing page 1 of 1</span>
                <div style="display: flex; gap: 0.5rem;">
                    <button class="page-btn" id="prev-btn">Previous</button>
                    <button class="page-btn" id="next-btn">Next</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Note Reader Modal -->
    <div class="modal-overlay" id="modal-overlay">
        <div class="modal-content">
            <div class="modal-header">
                <div class="modal-header-info">
                    <h3 class="modal-book-title" id="modal-book-title">Book Title</h3>
                    <div class="modal-metadata">
                        <span id="modal-date">Date</span>
                        <span id="modal-chapter">Chapter</span>
                        <span id="modal-pages">Pages Read</span>
                    </div>
                </div>
                <button class="close-btn" id="close-modal-btn">&times;</button>
            </div>
            <div class="modal-body markdown-body" id="modal-body">
                <!-- Rendered Markdown Content -->
            </div>
        </div>
    </div>

    <div class="tooltip" id="tooltip"></div>

    <script>
        const rawLogs = __LOGS_DATA__;

        // Current filter state
        let currentBookFilter = null;

        const lookbackInput = document.getElementById("lookback");
        const groupbySelect = document.getElementById("groupby");
        const chartDiv = document.getElementById("chart-div");
        const tooltip = document.getElementById("tooltip");
        
        const statTotal = document.getElementById("stat-total");
        const statAvg = document.getElementById("stat-avg");
        const statBooks = document.getElementById("stat-books");
        const statStreak = document.getElementById("stat-streak");

        const searchBox = document.getElementById("search-box");
        const tableBody = document.getElementById("table-body");
        const pageIndicator = document.getElementById("page-indicator");
        const prevBtn = document.getElementById("prev-btn");
        const nextBtn = document.getElementById("next-btn");

        const filterBanner = document.getElementById("filter-banner");
        const filterBookName = document.getElementById("filter-book-name");
        const clearFilterBtn = document.getElementById("clear-filter-btn");

        const modalOverlay = document.getElementById("modal-overlay");
        const modalBookTitle = document.getElementById("modal-book-title");
        const modalDate = document.getElementById("modal-date");
        const modalChapter = document.getElementById("modal-chapter");
        const modalPages = document.getElementById("modal-pages");
        const modalBody = document.getElementById("modal-body");
        const closeModalBtn = document.getElementById("close-modal-btn");

        // Helper functions for date operations
        function formatLocalISO(date) {
            const yyyy = date.getFullYear();
            const mm = String(date.getMonth() + 1).padStart(2, '0');
            const dd = String(date.getDate()).padStart(2, '0');
            return `${yyyy}-${mm}-${dd}`;
        }

        function parseLocalISO(dateStr) {
            if (!dateStr) return new Date();
            const parts = dateStr.split("-");
            if (parts.length < 3) return new Date();
            return new Date(parseInt(parts[0], 10), parseInt(parts[1], 10) - 1, parseInt(parts[2], 10));
        }

        function getStartOfWeek(dateStr) {
            const d = parseLocalISO(dateStr);
            const day = d.getDay();
            d.setDate(d.getDate() - day);
            return formatLocalISO(d);
        }

        // Get nice tick marks for Y axis
        function getNiceMaxAndInterval(rawMax) {
            const minMax = Math.max(10, rawMax);
            const magnitude = Math.pow(10, Math.floor(Math.log10(minMax)));
            const normalized = minMax / magnitude;
            
            let step;
            if (normalized <= 1.5) step = 0.2 * magnitude;
            else if (normalized <= 3.0) step = 0.5 * magnitude;
            else if (normalized <= 7.0) step = 1.0 * magnitude;
            else step = 2.0 * magnitude;
            
            const yMax = Math.ceil(minMax / step) * step;
            return { yMax, step };
        }

        // Get logs filtered by active book selection
        function getFilteredLogsByBook() {
            if (!currentBookFilter) return rawLogs;
            return rawLogs.filter(l => l.material === currentBookFilter);
        }

        // Calculate Overview Stats
        function calculateStats() {
            const logsToUse = getFilteredLogsByBook();
            if (logsToUse.length === 0) {
                statTotal.textContent = "0";
                statBooks.textContent = "0";
                statAvg.textContent = "0 p/d";
                statStreak.textContent = "0 days";
                return;
            }

            // Total Pages
            const total = logsToUse.reduce((acc, l) => acc + l.pages_read, 0);
            statTotal.textContent = total.toLocaleString();

            // Book count
            const uniqueBooks = new Set(logsToUse.map(l => l.material));
            statBooks.textContent = uniqueBooks.size;

            // Daily Average
            const dates = logsToUse.map(l => parseLocalISO(l.date).getTime());
            const minDate = new Date(Math.min(...dates));
            const maxDate = new Date(Math.max(...dates));
            const diffDays = Math.ceil((maxDate - minDate) / (1000 * 60 * 60 * 24)) + 1;
            const avg = Math.round(total / diffDays);
            statAvg.textContent = `${avg} p/d`;

            // Current Streak
            const activeDates = new Set(logsToUse.map(l => l.date));
            let streak = 0;
            let checkDate = new Date();
            if (!activeDates.has(formatLocalISO(checkDate))) {
                checkDate.setDate(checkDate.getDate() - 1);
            }
            
            while (activeDates.has(formatLocalISO(checkDate))) {
                streak++;
                checkDate.setDate(checkDate.getDate() - 1);
            }
            statStreak.textContent = `${streak} days`;
        }

        // Render SVG Chart
        function renderChart(numDays, groupBy) {
            chartDiv.innerHTML = "";
            const today = new Date();
            const logsToUse = getFilteredLogsByBook();
            
            function getGroupKey(dateStr) {
                if (groupBy === "day") return dateStr;
                if (groupBy === "week") return getStartOfWeek(dateStr);
                if (groupBy === "month") return dateStr.substring(0, 7);
                if (groupBy === "year") return dateStr.substring(0, 4);
                return dateStr;
            }

            // Initialize dataMap
            const dataMap = {};
            const groupsSet = new Set();
            for (let i = numDays - 1; i >= 0; i--) {
                const d = new Date();
                d.setDate(today.getDate() - i);
                const dateStr = formatLocalISO(d);
                groupsSet.add(getGroupKey(dateStr));
            }
            
            const sortedGroups = Array.from(groupsSet).sort();
            sortedGroups.forEach(g => {
                dataMap[g] = { pages: 0, books: {} };
            });

            // Aggregate
            logsToUse.forEach(log => {
                const groupKey = getGroupKey(log.date);
                if (groupKey in dataMap) {
                    dataMap[groupKey].pages += log.pages_read;
                    dataMap[groupKey].books[log.material] = (dataMap[groupKey].books[log.material] || 0) + log.pages_read;
                }
            });

            const chartData = Object.entries(dataMap).sort((a, b) => a[0].localeCompare(b[0]));

            // Dimensions
            const width = 800;
            const height = 245;
            const paddingLeft = 40;
            const paddingRight = 20;
            const paddingTop = 15;
            const paddingBottom = 55;
            
            const chartWidth = width - paddingLeft - paddingRight;
            const chartHeight = height - paddingTop - paddingBottom;
            
            const rawMax = Math.max(10, ...chartData.map(d => d[1].pages));
            const { yMax, step } = getNiceMaxAndInterval(rawMax);
            
            const barCount = chartData.length;
            const gapRatio = 0.25;
            const barWidth = chartWidth / (barCount * (1 + gapRatio) - gapRatio);
            const gapWidth = barWidth * gapRatio;
            
            let svgContent = `<svg width="100%" height="${height}" viewBox="0 0 ${width} ${height}" style="font-size: 10px; fill: var(--text-muted);">`;
            
            // Grid lines & Y ticks
            for (let val = 0; val <= yMax; val += step) {
                const y = paddingTop + chartHeight - (val / yMax) * chartHeight;
                svgContent += `
                    <line x1="${paddingLeft}" y1="${y}" x2="${width - paddingRight}" y2="${y}" stroke="var(--border)" stroke-width="1" stroke-dasharray="2,2" />
                    <text x="${paddingLeft - 8}" y="${y + 3}" text-anchor="end" fill="var(--text-muted)">${val}</text>
                `;
            }

            const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
            let lastMonthStr = "";
            let lastYearStr = "";

            chartData.forEach(([dateStr, valData], index) => {
                const x = paddingLeft + index * (barWidth + gapWidth);
                const val = valData.pages;
                const barHeight = (val / yMax) * chartHeight;
                const y = paddingTop + chartHeight - barHeight;
                
                const color = val > 0 ? "var(--accent)" : "transparent";
                
                let dayStr = "";
                let monthStr = "";
                let monthName = "";
                let yearStr = "";
                
                if (groupBy === "day" || groupBy === "week") {
                    const dateParts = dateStr.split("-");
                    dayStr = parseInt(dateParts[2], 10).toString();
                    monthStr = dateParts[1];
                    monthName = monthNames[parseInt(monthStr, 10) - 1] || monthStr;
                    yearStr = dateParts[0];
                } else if (groupBy === "month") {
                    const dateParts = dateStr.split("-");
                    monthStr = dateParts[1];
                    monthName = monthNames[parseInt(monthStr, 10) - 1] || monthStr;
                    yearStr = dateParts[0];
                } else if (groupBy === "year") {
                    yearStr = dateStr;
                }
                
                const showMonth = monthName && (index === 0 || monthStr !== lastMonthStr || yearStr !== lastYearStr);
                const showYear = yearStr && (index === 0 || yearStr !== lastYearStr);
                
                if (showMonth) lastMonthStr = monthStr;
                if (showYear) lastYearStr = yearStr;
                
                let labelTooltip = dateStr;
                if (groupBy === "week") {
                    const weekEndObj = parseLocalISO(dateStr);
                    weekEndObj.setDate(weekEndObj.getDate() + 6);
                    const weekEndStr = formatLocalISO(weekEndObj);
                    labelTooltip = `Week of ${dateStr} to ${weekEndStr}`;
                } else if (groupBy === "month") {
                    labelTooltip = `${monthName} ${yearStr}`;
                } else if (groupBy === "year") {
                    labelTooltip = `${yearStr}`;
                }
                
                const booksList = Object.keys(valData.books).length > 0 
                    ? "\\n" + Object.entries(valData.books).map(([b, p]) => `• ${b}: ${p} pages`).join("\\n") 
                    : "";
                const tooltipText = `**${labelTooltip}**\\nTotal: ${val} pages${booksList}`;
                
                svgContent += `
                    <g class="bar-group">
                        <rect class="bar-item" data-tooltip="${tooltipText}" x="${x}" y="${y}" width="${barWidth}" height="${barHeight}" fill="${color}" rx="3" ry="3" style="transition: fill-opacity 0.15s; cursor: pointer;"></rect>
                        <text x="${x + barWidth / 2}" y="${height - paddingBottom + 14}" text-anchor="middle" style="font-size: 8px; fill: var(--text-muted); pointer-events: none;">${dayStr}</text>
                        ${showMonth ? `
                        <line x1="${x + barWidth / 2}" y1="${height - paddingBottom + 18}" x2="${x + barWidth / 2}" y2="${height - paddingBottom + 20}" stroke="var(--border)" stroke-width="1" />
                        <text x="${x + barWidth / 2}" y="${height - paddingBottom + 30}" text-anchor="middle" style="font-weight: 600; fill: var(--text-main); font-size: 9px; pointer-events: none;">${monthName}</text>
                        ` : ""}
                        ${showYear ? `
                        <line x1="${x + barWidth / 2}" y1="${height - paddingBottom + 33}" x2="${x + barWidth / 2}" y2="${height - paddingBottom + 35}" stroke="var(--border)" stroke-width="1" />
                        <text x="${x + barWidth / 2}" y="${height - paddingBottom + 45}" text-anchor="middle" style="font-weight: 600; fill: var(--text-main); font-size: 9px; pointer-events: none;">${yearStr}</text>
                        ` : ""}
                    </g>
                `;
            });
            
            svgContent += '</svg>';
            chartDiv.innerHTML = svgContent;
        }

        // Table logic
        let currentPage = 1;
        const rowsPerPage = 10;
        let filteredLogs = [...rawLogs];

        function filterAndRenderTable() {
            const query = searchBox.value.toLowerCase().trim();
            const logsToUse = getFilteredLogsByBook();

            filteredLogs = logsToUse.filter(l => 
                l.material.toLowerCase().includes(query) || 
                (l.chapter && l.chapter.toLowerCase().includes(query)) ||
                l.date.includes(query)
            );
            
            currentPage = 1;
            renderTable();
        }

        function renderTable() {
            tableBody.innerHTML = "";
            const start = (currentPage - 1) * rowsPerPage;
            const end = start + rowsPerPage;
            const pageData = filteredLogs.slice(start, end);

            pageData.forEach(row => {
                const tr = document.createElement("tr");
                tr.className = "note-row";
                
                // Show view notes button only if there is a note body
                const hasNotes = row.note_body && row.note_body.trim().length > 0;
                const notesBtnCell = hasNotes 
                    ? `<td style="text-align: center;"><button class="note-btn" onclick="openNoteReader('${row.date}', '${row.material.replace(/'/g, "\\'")}', '${(row.chapter || "").replace(/'/g, "\\'")}', ${row.pages_read}, '${row.page_range}')">📖 View</button></td>` 
                    : `<td style="text-align: center; color: var(--text-muted); font-size: 0.8rem;">-</td>`;
                
                tr.innerHTML = `
                    <td>${row.date}</td>
                    <td><a class="book-link" onclick="setBookFilter('${row.material.replace(/'/g, "\\'")}')">${row.material}</a></td>
                    <td style="color: var(--text-muted);">${row.chapter || '-'}</td>
                    <td>${row.page_range || '-'}</td>
                    <td style="font-weight: 600; color: var(--accent);">${row.pages_read}</td>
                    ${notesBtnCell}
                `;
                tableBody.appendChild(tr);
            });

            const totalPages = Math.ceil(filteredLogs.length / rowsPerPage) || 1;
            pageIndicator.textContent = `Showing page ${currentPage} of ${totalPages}`;
            
            prevBtn.disabled = currentPage === 1;
            nextBtn.disabled = currentPage === totalPages;
        }

        // Set book filter
        window.setBookFilter = function(bookName) {
            currentBookFilter = bookName;
            filterBookName.textContent = bookName;
            filterBanner.style.display = "flex";
            
            // Re-render everything
            calculateStats();
            renderChart(parseInt(lookbackInput.value, 10), groupbySelect.value);
            filterAndRenderTable();
        }

        // Clear book filter
        function clearBookFilter() {
            currentBookFilter = null;
            filterBanner.style.display = "none";
            
            // Re-render everything
            calculateStats();
            renderChart(parseInt(lookbackInput.value, 10), groupbySelect.value);
            filterAndRenderTable();
        }

        // Note Reader modal controls
        window.openNoteReader = function(date, book, chapter, pages, range) {
            // Find note in logs
            const matchedLog = rawLogs.find(l => l.date === date && l.material === book && l.pages_read === pages);
            if (matchedLog && matchedLog.note_body) {
                modalBookTitle.textContent = book;
                modalDate.textContent = `📅 ${date}`;
                modalChapter.textContent = chapter ? `📖 ${chapter}` : "";
                modalPages.textContent = `📄 Read ${pages} pages (${range || '-'})`;
                
                // Parse markdown into HTML
                modalBody.innerHTML = marked.parse(matchedLog.note_body);
                
                modalOverlay.style.display = "flex";
                document.body.style.overflow = "hidden"; // Disable background scrolling
            }
        }

        function closeModal() {
            modalOverlay.style.display = "none";
            document.body.style.overflow = ""; // Re-enable scrolling
        }

        // Event Listeners for controls
        lookbackInput.addEventListener("input", (e) => {
            const val = parseInt(e.target.value, 10);
            if (val > 0) {
                renderChart(val, groupbySelect.value);
            }
        });

        groupbySelect.addEventListener("change", (e) => {
            const val = e.target.value;
            let defaultDays = 30;
            if (val === "day") defaultDays = 30;
            else if (val === "week") defaultDays = 90;
            else if (val === "month") defaultDays = 365;
            else if (val === "year") defaultDays = 3650;
            
            lookbackInput.value = defaultDays;
            renderChart(defaultDays, val);
        });

        searchBox.addEventListener("input", filterAndRenderTable);
        clearFilterBtn.addEventListener("click", clearBookFilter);
        closeModalBtn.addEventListener("click", closeModal);
        
        // Close modal on overlay tap
        modalOverlay.addEventListener("click", (e) => {
            if (e.target === modalOverlay) {
                closeModal();
            }
        });

        // Close modal on ESC key
        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape") {
                closeModal();
            }
        });

        prevBtn.addEventListener("click", () => {
            if (currentPage > 1) {
                currentPage--;
                renderTable();
            }
        });

        nextBtn.addEventListener("click", () => {
            const totalPages = Math.ceil(filteredLogs.length / rowsPerPage) || 1;
            if (currentPage < totalPages) {
                currentPage++;
                renderTable();
            }
        });

        // Hover Tooltip Interactions
        function showTooltip(e, content) {
            tooltip.innerHTML = content.replace(/\\*\\*(.*?)\\*\\*/g, "<strong>$1</strong>");
            tooltip.style.display = "block";
        }

        function moveTooltip(clientX, clientY) {
            tooltip.style.left = `${clientX + 15}px`;
            tooltip.style.top = `${clientY + 15}px`;
        }

        function hideTooltip() {
            tooltip.style.display = "none";
        }

        chartDiv.addEventListener("mouseover", (e) => {
            if (e.target.classList.contains("bar-item")) {
                const text = e.target.getAttribute("data-tooltip");
                if (text) showTooltip(e, text);
            }
        });

        chartDiv.addEventListener("mousemove", (e) => {
            if (tooltip.style.display === "block") {
                moveTooltip(e.clientX, e.clientY);
            }
        });

        chartDiv.addEventListener("mouseout", (e) => {
            if (e.target.classList.contains("bar-item")) {
                hideTooltip();
            }
        });

        // Touch interactions
        chartDiv.addEventListener("touchstart", (e) => {
            if (e.target.classList.contains("bar-item")) {
                const text = e.target.getAttribute("data-tooltip");
                if (text) {
                    showTooltip(e, text);
                    const rect = e.target.getBoundingClientRect();
                    tooltip.style.left = `${rect.left + window.scrollX}px`;
                    tooltip.style.top = `${rect.top + window.scrollY - tooltip.offsetHeight - 10}px`;
                }
            }
        }, { passive: true });

        document.addEventListener("touchstart", (e) => {
            if (!chartDiv.contains(e.target) && !tooltip.contains(e.target)) {
                hideTooltip();
            }
        }, { passive: true });

        // Initial setup
        calculateStats();
        renderChart(30, "day");
        filterAndRenderTable();
    </script>
</body>
</html>
"""

html_content = html_template.replace("__LOGS_DATA__", json.dumps(logs_data))

# Create dist directory
dist_dir = os.path.join(vault_path, "dist")
os.makedirs(dist_dir, exist_ok=True)

with open(os.path.join(dist_dir, "index.html"), "w", encoding="utf-8") as f:
    f.write(html_content)

with open(os.path.join(dist_dir, ".nojekyll"), "w", encoding="utf-8") as f:
    f.write("\n")

print(f"Generated static index.html and .nojekyll with {len(logs_data)} reading logs inside dist/!")
