---
name: update_bulletin
description: Reads boletim.pdf and updates the landing page index.html with the new week's sermon, agenda, birthdays, prayer requests, and gallery images.
---

You have been activated to update the church landing page with a new bulletin. Follow the guidelines in the workspace's [UPDATE.md](file:///f:/bulletin-renderer/UPDATE.md) file.

### Summary of Tasks:
1. **Extract Content**: Execute Python commands to extract the text from the new `boletim.pdf` into a temporary text file, and verify the images have been extracted into `assets/boletim-images/`.
2. **Analyze Content**: Find the issue metadata, sermon content, weekly schedule/agenda, services scales (Louvor and Junta Diaconal duties), birthdays, prayer list, PIX key, and leadership names.
3. **Update HTML**: Open `index.html` and statically replace the text, timeline, birthdays, prayer wall tags, leadership lists, and image gallery references. Ensure the visual styles and interactivity from `styles.css` and `app.js` are preserved without regressions.
4. **Verify**: Launch a local web server (port 5500), inspect the landing page visually using the browser, click the copy CNPJ button, open the lightbox, and review responsive margins.

Always reference [UPDATE.md](file:///f:/bulletin-renderer/UPDATE.md) for detailed instructions.
