import fs from 'fs';
import matter from 'gray-matter';
import { markdownToBlocks } from '@tryfabric/martian';

const content = process.argv[2];
const matterResult = matter(content);
const blocks = markdownToBlocks(matterResult.content, {strictImageUrls: false});

fs.writeFileSync(process.argv[3], JSON.stringify(blocks, null, 2));
