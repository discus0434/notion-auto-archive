import fetch from "node-fetch";
import { Readability } from "@mozilla/readability";
import { JSDOM } from "jsdom";
import fs from "fs";

// get the article content
async function getArticleContentFromURL(url) {
  const response = await fetch(url);
  const html = await response.text();
  const doc = new JSDOM(html).window.document;
  const reader = new Readability(doc);
  const article = reader.parse();
  return article;
}

// read the article content from a file
function getArticleContentFromFile(path) {
  const html = fs.readFileSync(path, "utf8");
  const doc = new JSDOM(html).window.document;
  const reader = new Readability(doc);
  const article = reader.parse();
  return article;
}

/////////////////////////////////////////////////////////
// main function
/////////////////////////////////////////////////////////

// if path is given, read the article content from a file
// otherwise, get the article content from a URL
let article;

if (process.argv[2].startsWith("http")) {
  article = getArticleContentFromURL(process.argv[2]);
} else {
  article = getArticleContentFromFile(process.argv[2]);
}

// write the article content to a file
fs.writeFileSync(process.argv[3], JSON.stringify(article));
