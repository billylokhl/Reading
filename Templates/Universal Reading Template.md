<%*
const noteType = await tp.system.suggester(["New Reading Material (Book/Article)", "New Reading Session (Log)"], ["material", "log"]);

if (noteType === "material") {
    const title = await tp.system.prompt("Title of the material:");
    if (!title) return;
    const author = await tp.system.prompt("Author:") || "";
    const materialType = await tp.system.suggester(["Book", "Article", "Paper"], ["Book", "Article", "Paper"]) || "Book";
    
    const targetFolder = "Reading Materials";
    if (!app.vault.getAbstractFileByPath(targetFolder)) {
        await app.vault.createFolder(targetFolder);
    }

    const targetPath = targetFolder + "/" + title;
    if (app.vault.getAbstractFileByPath(targetPath + ".md")) {
        new Notice("Error: A note for '" + title + "' already exists in Reading Materials!");
        return;
    }
    
    await tp.file.move(targetPath);
    
    let content = "---\n" +
"type: material\n" +
"material_type: " + materialType + "\n" +
"title: \"" + title + "\"\n" +
"author: \"" + author + "\"\n" +
"status: reading\n" +
"---\n" +
"# " + title + (author ? " by " + author : "") + "\n\n" +
"## My Reading Logs\n" +
"```dataview\n" +
"TABLE date AS \"Date\", chapter AS \"Chapter\", page_range AS \"Pages\", pages_read AS \"Count\"\n" +
"FROM \"Reading Logs\"\n" +
"WHERE material = [[" + title + "]]\n" +
"SORT date DESC\n" +
"```\n";

    tR += content;
} else if (noteType === "log") {
    const today = tp.date.now("YYYY-MM-DD");
    
    // Dynamically list all files in the 'Reading Materials' folder
    const files = app.vault.getMarkdownFiles().filter(f => f.path.startsWith("Reading Materials/"));
    const bookTitles = files.map(f => f.basename);
    
    let material = "";
    if (bookTitles.length > 0) {
        material = await tp.system.suggester(bookTitles, bookTitles);
    } else {
        material = await tp.system.prompt("What are you reading? (Enter exact title):");
    }
    
    if (!material) return;
    const chapter = await tp.system.prompt("Chapter/Section:") || "";
    
    const startPageStr = await tp.system.prompt("Start Page (or leave blank):");
    const endPageStr = await tp.system.prompt("End Page (or leave blank):");
    
    let pagesRead = 0;
    let pageRange = "";
    
    const startPage = parseInt(startPageStr);
    const endPage = parseInt(endPageStr);
    
    if (!isNaN(startPage) && !isNaN(endPage)) {
        pagesRead = endPage - startPage + 1;
        pageRange = startPage + "-" + endPage;
    } else {
        const totalPagesStr = await tp.system.prompt("Total Pages Read (number):");
        pagesRead = parseInt(totalPagesStr) || 0;
        pageRange = pagesRead ? pagesRead.toString() : "";
    }
    
    const filename = today + " - " + (chapter ? chapter : "Reading Log");
    const targetFolder = "Reading Logs/" + material;
    
    if (!app.vault.getAbstractFileByPath(targetFolder)) {
        await app.vault.createFolder(targetFolder);
    }

    const targetPath = targetFolder + "/" + filename;
    if (app.vault.getAbstractFileByPath(targetPath + ".md")) {
        new Notice("Error: This reading log already exists!");
        return;
    }
    
    await tp.file.move(targetPath);
    
    let content = "---\n" +
"type: reading-log\n" +
"date: " + today + "\n" +
"material: \"[[" + material + "]]\"\n" +
"chapter: \"" + chapter + "\"\n" +
"page_range: \"" + pageRange + "\"\n" +
"pages_read: " + pagesRead + "\n" +
"---\n" +
"# " + (chapter ? chapter : "Reading Notes") + "\n\n" +
"## Notes\n" +
"- \n";

    tR += content;
}
-%>
