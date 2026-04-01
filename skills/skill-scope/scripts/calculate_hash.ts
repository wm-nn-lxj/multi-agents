#!/usr/bin/env npx ts-node
import { readFileSync, readdirSync } from "fs";
import { join, dirname } from "path";
import { createHash } from "crypto";
import { fileURLToPath } from "url";

const IGNORE_DIRS = new Set([".github", ".git", "__pycache__", "tests"]);
const IGNORE_FILES = new Set([
  "LICENSE.txt",
  "LICENSE",
  "README.md",
  "_meta.json",
  "pytest.ini",
  "requirements.txt",
  ".gitignore",
  ".env.example",
]);

function calculateFileSha256(filePath: string): string {
  const hashSha256 = createHash("sha256");
  try {
    const content = readFileSync(filePath, "utf-8");
    hashSha256.update(content);
    return hashSha256.digest("hex");
  } catch (e) {
    return `Error: ${e}`;
  }
}

function calculateStringSha256(inputString: string): string {
  return createHash("sha256").update(inputString).digest("hex");
}

function calculateProjectHash(projectPath: string): string {
  const fileHashes: string[] = [];

  function walkDir(dir: string): void {
    const entries = readdirSync(dir, { withFileTypes: true });
    const dirs: string[] = [];
    const files: string[] = [];

    for (const entry of entries) {
      if (entry.isDirectory()) {
        if (!IGNORE_DIRS.has(entry.name)) {
          dirs.push(entry.name);
        }
      } else if (entry.isFile()) {
        if (!IGNORE_FILES.has(entry.name)) {
          files.push(entry.name);
        }
      }
    }

    for (const filename of files) {
      const fpath = join(dir, filename);
      fileHashes.push(calculateFileSha256(fpath));
    }

    for (const d of dirs) {
      walkDir(join(dir, d));
    }
  }

  walkDir(projectPath);
  fileHashes.sort();
  return calculateStringSha256(fileHashes.join("\n"));
}

const isMain = (() => {
  const currentFile = fileURLToPath(import.meta.url);
  return process.argv[1] === currentFile || process.argv[1]?.endsWith("calculate_hash.ts");
})();

if (isMain) {
  const args = process.argv.slice(2);
  if (args.length !== 1) {
    console.error("Usage: npx tsx calculate_hash.ts <skill_directory>");
    process.exit(1);
  }

  const targetDir = args[0];

  try {
    const resultHash = calculateProjectHash(targetDir);
    if (resultHash) {
      console.log(resultHash);
    } else {
      console.error("Error: No valid files found in directory to calculate hash.");
      process.exit(1);
    }
  } catch (e) {
    console.error(`Error: Calculation failed: ${e}`);
    process.exit(1);
  }
}