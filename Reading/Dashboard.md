# 📚 Reading Dashboard

## 📈 Pages Read Over Time

```dataviewjs
const container = dv.el("div", "");

// Set styling programmatically on all containers to bypass Obsidian's HTML sanitizer
const inputContainer = container.createEl("div");
inputContainer.style.display = "flex";
inputContainer.style.alignItems = "center";
inputContainer.style.gap = "40px";
inputContainer.style.marginBottom = "20px";

const lookbackGroup = inputContainer.createEl("div");
lookbackGroup.style.display = "flex";
lookbackGroup.style.alignItems = "center";
lookbackGroup.style.gap = "8px";

lookbackGroup.createEl("span", { text: "Look back: " });
const input = lookbackGroup.createEl("input", {
    type: "number",
    value: "30"
});
input.style.width = "70px";
input.style.padding = "4px";
input.style.borderRadius = "4px";
input.style.border = "1px solid var(--background-modifier-border)";
input.style.background = "var(--background-primary)";
input.style.color = "var(--text-normal)";
lookbackGroup.createEl("span", { text: " days" });

const groupbyGroup = inputContainer.createEl("div");
groupbyGroup.style.display = "flex";
groupbyGroup.style.alignItems = "center";
groupbyGroup.style.gap = "8px";

groupbyGroup.createEl("span", { text: "Group by: " });
const select = groupbyGroup.createEl("select");
select.style.padding = "4px";
select.style.borderRadius = "4px";
select.style.border = "1px solid var(--background-modifier-border)";
select.style.background = "var(--background-primary)";
select.style.color = "var(--text-normal)";

select.createEl("option", { value: "day", text: "Day" });
select.createEl("option", { value: "week", text: "Week" });
select.createEl("option", { value: "month", text: "Month" });
select.createEl("option", { value: "year", text: "Year" });

// Programmatically set style properties to bypass Obsidian's HTML sanitizer
const tooltip = container.createEl("div");
tooltip.style.position = "fixed";
tooltip.style.display = "none";
tooltip.style.backgroundColor = "var(--background-secondary-alt)";
tooltip.style.color = "var(--text-normal)";
tooltip.style.padding = "8px 12px";
tooltip.style.borderRadius = "6px";
tooltip.style.border = "1px solid var(--background-modifier-border)";
tooltip.style.boxShadow = "0 4px 6px rgba(0,0,0,0.15)";
tooltip.style.pointerEvents = "none";
tooltip.style.zIndex = "2000";
tooltip.style.fontSize = "11px";
tooltip.style.lineHeight = "1.4";
tooltip.style.whiteSpace = "pre-line";

const chartDiv = container.createEl("div");

// Safe formatting of local dates (YYYY-MM-DD)
function formatLocalISO(date) {
    const yyyy = date.getFullYear();
    const mm = String(date.getMonth() + 1).padStart(2, '0');
    const dd = String(date.getDate()).padStart(2, '0');
    return `${yyyy}-${mm}-${dd}`;
}

// Safe parsing of YYYY-MM-DD strings
function parseLocalISO(dateStr) {
    if (!dateStr) return new Date();
    const parts = dateStr.split("-");
    if (parts.length < 3) return new Date();
    return new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]));
}

function getStartOfWeek(dateStr) {
    const d = parseLocalISO(dateStr);
    const day = d.getDay(); // 0 is Sunday
    d.setDate(d.getDate() - day);
    return formatLocalISO(d);
}

// Generate nice tick marks for Y axis
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

function renderChart(numDays, groupBy) {
    chartDiv.innerHTML = ""; // clear previous
    
    // Get all reading logs
    const logs = dv.pages('"Reading Logs"')
        .where(p => p.type === 'reading-log' && p.date && p.pages_read !== undefined);
        
    // Parse dates and sum by date/group
    const dataMap = {};
    const today = new Date();
    
    // Helper to get group key
    function getGroupKey(dateStr) {
        if (groupBy === "day") return dateStr;
        if (groupBy === "week") return getStartOfWeek(dateStr);
        if (groupBy === "month") return dateStr.substring(0, 7); // YYYY-MM
        if (groupBy === "year") return dateStr.substring(0, 4); // YYYY
        return dateStr;
    }
    
    // Initialize days/groups in range
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
    
    // Aggregate pages read and books
    logs.forEach(log => {
        let logDateStr = "";
        if (log.date && log.date.toString) {
            const str = log.date.toString();
            const match = str.match(/\d{4}-\d{2}-\d{2}/);
            if (match) logDateStr = match[0];
        }
        if (logDateStr) {
            const groupKey = getGroupKey(logDateStr);
            if (groupKey in dataMap) {
                const pr = Number(log.pages_read) || 0;
                dataMap[groupKey].pages += pr;
                
                let mat = "";
                if (log.material) {
                    if (log.material.path) {
                        mat = log.material.display || log.material.path.split("/").pop().replace(".md", "");
                    } else {
                        mat = log.material.toString().replace(/\[\[|\]\]/g, "");
                    }
                }
                if (mat) {
                    dataMap[groupKey].books[mat] = (dataMap[groupKey].books[mat] || 0) + pr;
                }
            }
        }
    });
    
    const chartData = Object.entries(dataMap).sort((a, b) => a[0].localeCompare(b[0]));
    
    // Render SVG
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
    const gapRatio = 0.25; // 25% gap
    const barWidth = chartWidth / (barCount * (1 + gapRatio) - gapRatio);
    const gapWidth = barWidth * gapRatio;
    
    let svgContent = `<svg width="100%" height="${height}" viewBox="0 0 ${width} ${height}" style="font-family: var(--font-interface); font-size: 10px; fill: var(--text-muted);">`;
    
    // Grid lines & Y ticks (Regular nice step values)
    for (let val = 0; val <= yMax; val += step) {
        const y = paddingTop + chartHeight - (val / yMax) * chartHeight;
        svgContent += `
            <line x1="${paddingLeft}" y1="${y}" x2="${width - paddingRight}" y2="${y}" stroke="var(--background-modifier-border)" stroke-width="0.5" stroke-dasharray="2,2" />
            <text x="${paddingLeft - 8}" y="${y + 3}" text-anchor="end">${val}</text>
        `;
    }
    
    // Track labels
    let lastMonthStr = "";
    let lastYearStr = "";
    const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    
    // Bars and X labels
    chartData.forEach(([dateStr, valData], index) => {
        const x = paddingLeft + index * (barWidth + gapWidth);
        const val = valData.pages;
        const barHeight = (val / yMax) * chartHeight;
        const y = paddingTop + chartHeight - barHeight;
        
        const color = val > 0 ? "var(--interactive-accent, #6366f1)" : "transparent";
        
        // Resolve date label strings
        let dayStr = "";
        let monthStr = "";
        let monthName = "";
        let yearStr = "";
        
        if (groupBy === "day" || groupBy === "week") {
            const dateParts = dateStr.split("-");
            dayStr = parseInt(dateParts[2]).toString();
            monthStr = dateParts[1];
            monthName = monthNames[parseInt(monthStr) - 1] || monthStr;
            yearStr = dateParts[0];
        } else if (groupBy === "month") {
            const dateParts = dateStr.split("-"); // YYYY-MM
            dayStr = "";
            monthStr = dateParts[1];
            monthName = monthNames[parseInt(monthStr) - 1] || monthStr;
            yearStr = dateParts[0];
        } else if (groupBy === "year") {
            dayStr = "";
            monthStr = "";
            monthName = "";
            yearStr = dateStr; // YYYY
        }
        
        // Conditions for month and year labels
        const showMonth = monthName && (index === 0 || monthStr !== lastMonthStr || yearStr !== lastYearStr);
        const showYear = yearStr && (index === 0 || yearStr !== lastYearStr);
        
        if (showMonth) lastMonthStr = monthStr;
        if (showYear) lastYearStr = yearStr;
        
        // Format Tooltip Text
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
            ? "\n" + Object.entries(valData.books).map(([b, p]) => `• ${b}: ${p} pages`).join("\n") 
            : "";
        const tooltipText = `**${labelTooltip}**\nTotal: ${val} pages${booksList}`;
        
        svgContent += `
            <g class="bar-group">
                <rect class="bar-item" data-tooltip="${tooltipText}" x="${x}" y="${y}" width="${barWidth}" height="${barHeight}" fill="${color}" rx="2" ry="2" style="transition: fill-opacity 0.15s; cursor: pointer;"></rect>
                
                <!-- Day label -->
                <text x="${x + barWidth / 2}" y="${height - paddingBottom + 14}" text-anchor="middle" style="font-size: 8px; pointer-events: none;">${dayStr}</text>
                
                <!-- Month label -->
                ${showMonth ? `
                <line x1="${x + barWidth / 2}" y1="${height - paddingBottom + 18}" x2="${x + barWidth / 2}" y2="${height - paddingBottom + 20}" stroke="var(--background-modifier-border)" stroke-width="0.5" />
                <text x="${x + barWidth / 2}" y="${height - paddingBottom + 30}" text-anchor="middle" style="font-weight: bold; fill: var(--text-normal); font-size: 9px; pointer-events: none;">${monthName}</text>
                ` : ""}
                
                <!-- Year label -->
                ${showYear ? `
                <line x1="${x + barWidth / 2}" y1="${height - paddingBottom + 33}" x2="${x + barWidth / 2}" y2="${height - paddingBottom + 35}" stroke="var(--background-modifier-border)" stroke-width="0.5" />
                <text x="${x + barWidth / 2}" y="${height - paddingBottom + 45}" text-anchor="middle" style="font-weight: bold; fill: var(--text-normal); font-size: 9px; pointer-events: none;">${yearStr}</text>
                ` : ""}
            </g>
        `;
    });
    
    svgContent += '</svg>';
    chartDiv.innerHTML = svgContent;
}

// Initial render
renderChart(30, "day");

// Handle changes
input.addEventListener("input", (e) => {
    const val = parseInt(e.target.value);
    if (val > 0) {
        renderChart(val, select.value);
    }
});

select.addEventListener("change", (e) => {
    const val = e.target.value;
    let defaultDays = 30;
    if (val === "day") defaultDays = 30;
    else if (val === "week") defaultDays = 90;
    else if (val === "month") defaultDays = 365;
    else if (val === "year") defaultDays = 3650;
    
    input.value = defaultDays;
    renderChart(defaultDays, val);
});

// Tooltip hover interactions (Desktop)
chartDiv.addEventListener("mouseover", (e) => {
    if (e.target.classList.contains("bar-item")) {
        const tooltipText = e.target.getAttribute("data-tooltip");
        if (tooltipText) {
            tooltip.innerHTML = tooltipText.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
            tooltip.style.display = "block";
            e.target.style.fillOpacity = "0.75";
        }
    }
});

chartDiv.addEventListener("mouseout", (e) => {
    if (e.target.classList.contains("bar-item")) {
        tooltip.style.display = "none";
        e.target.style.fillOpacity = "1.0";
    }
});

chartDiv.addEventListener("mousemove", (e) => {
    tooltip.style.left = `${e.clientX + 15}px`;
    tooltip.style.top = `${e.clientY + 15}px`;
});

// Touch support (Obsidian Mobile / iPhone)
chartDiv.addEventListener("touchstart", (e) => {
    if (e.target.classList.contains("bar-item")) {
        const tooltipText = e.target.getAttribute("data-tooltip");
        if (tooltipText) {
            tooltip.innerHTML = tooltipText.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
            tooltip.style.display = "block";
            
            // Position tooltip above the touched bar
            const rect = e.target.getBoundingClientRect();
            tooltip.style.left = `${rect.left + window.scrollX}px`;
            tooltip.style.top = `${rect.top + window.scrollY - tooltip.offsetHeight - 10}px`;
            e.target.style.fillOpacity = "0.75";
        }
    }
}, { passive: true });

chartDiv.addEventListener("touchend", (e) => {
    if (e.target.classList.contains("bar-item")) {
        e.target.style.fillOpacity = "1.0";
    }
}, { passive: true });

// Hide tooltip if user taps outside the chart area
document.addEventListener("touchstart", (e) => {
    if (!chartDiv.contains(e.target) && !tooltip.contains(e.target)) {
        tooltip.style.display = "none";
    }
}, { passive: true });
```

## 🗓️ Reading Heatmap (This Month)

```tracker
searchType: frontmatter, frontmatter
searchTarget: date, pages_read
folder: Reading Logs
xDataset: 0
datasetName: date, Pages Read
month:
    startWeekOn: 'Sun'
    color: '#10b981'
    showSelectedValue: true
```

## 📖 Currently Reading

```dataview
TABLE author AS "Author", material_type AS "Type"
FROM "Reading Materials"
WHERE status = "reading"
```

## 📝 Recent Reading Logs

```dataview
TABLE 
  material AS "Reading Material", 
  chapter AS "Chapter/Section", 
  page_range AS "Pages",
  pages_read AS "Pages Read"
FROM "Reading Logs"
WHERE type = "reading-log"
SORT date DESC
LIMIT 10
```
