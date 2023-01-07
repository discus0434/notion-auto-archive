import fetch from "node-fetch";
import { Readability } from "@mozilla/readability";
import { JSDOM } from "jsdom";
import fs from "fs";
import matter from "gray-matter";
import TurndownService from "turndown";
import { markdownToBlocks } from "@tryfabric/martian";

// get the article content
export async function getArticleContentFromURL(url) {
  const response = await fetch(url);
  const html = await response.text();
  const doc = new JSDOM(html).window.document;
  const reader = new Readability(doc);
  const article = reader.parse();
  return article;
}

getArticleContentFromURL(process.argv[2]).then((article) => {
  // convert the article content to markdown
  const turndownService = new TurndownService();
  const markdown = turndownService.turndown(article.content);
  // parse the article content with gray-matter
  const matterResult = matter(markdown);
  // convert the article content to Notion blocks
  const blocks = markdownToBlocks(matterResult.content, {
    strictImageUrls: false,
  });
  // write the article content, markdown and blocks to a file
  fs.writeFileSync(
    process.argv[3],
    JSON.stringify({
      article,
      markdown,
      blocks,
    })
  );
});
