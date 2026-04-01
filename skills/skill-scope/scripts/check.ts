#!/usr/bin/env npx ts-node
import { readFileSync } from "fs";
import { dirname } from "path";
import { randomBytes } from "crypto";

const MAX_QUESTION_LENGTH = 2000;

const ENV_FILE_PATH = '/home/sandbox/.openclaw/.xiaoyienv';
const API_URL_SUFFIX = '/celia-claw/v1/rest-api/skill/execute';
const SKILL_ID = 'skill-scope';

interface EnvConfig {
  apiKey: string;
  uid: string;
  serviceUrl: string;
}

function loadEnvConfig(): EnvConfig {
  const config: EnvConfig = {
    apiKey: '',
    uid: '',
    serviceUrl: ''
  };

  try {
    const content = readFileSync(ENV_FILE_PATH, 'utf-8');
    const lines = content.split('\n');
    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('#')) continue;
      const [key, ...valueParts] = trimmed.split('=');
      if (key && valueParts.length > 0) {
        const value = valueParts.join('=').trim();
        if (key === 'PERSONAL-API-KEY') config.apiKey = value;
        if (key === 'PERSONAL-UID') config.uid = value;
        if (key === 'SERVICE_URL') config.serviceUrl = value;
      }
    }
  } catch {
  }

  return config;
}

function buildQuestionText(
  targetHash: string,
  skillContent: string = "",
  url: string = ""
): string {
  const data: Record<string, string> = { 
    subSceneID: "AI_AGENT_RUNTIME_XIAOYICLAW_SKILL_SCAN",
    hash: targetHash,
    url: url || "",
    skill: ""
  };

  const baseJson = JSON.stringify(data);
  const baseLength = baseJson.length;
  const available = MAX_QUESTION_LENGTH - baseLength;

  if (skillContent) {
    if (skillContent.length > available) {
      skillContent = skillContent.substring(0, available);
    }
    data.skill = skillContent;
  }

  let questionText = JSON.stringify(data);

  if (questionText.length > MAX_QUESTION_LENGTH) {
    questionText = questionText.substring(0, MAX_QUESTION_LENGTH);
  }

  return questionText;
}

function generateTraceId(): string {
    return randomBytes(16).toString('hex');
}

async function callAsApi(
  targetHash: string,
  skillContent: string = "",
  url: string = ""
): Promise<string> {
  const envConfig = loadEnvConfig();
  const questionText = buildQuestionText(targetHash, skillContent, url);

  if (!envConfig.serviceUrl) {
    throw new Error("SERVICE_URL is not configured");
  }

  const apiUrl = envConfig.serviceUrl + API_URL_SUFFIX;
  const headers: Record<string, string> = {
    'x-hag-trace-id': generateTraceId(),
    'x-uid': envConfig.uid,
    'x-api-key': envConfig.apiKey,
    'x-request-from': 'openclaw',
    'x-skill-id': SKILL_ID,
    'Content-Type': 'application/json'
  };

  const body = JSON.stringify({
    questionText: questionText,
    textSource: "question",
    action: "SKILL_SCAN",
  });

  const response = await fetch(apiUrl, {
    method: "POST",
    headers,
    body,
  });

  if (!response.ok) {
    throw new Error(`API request failed with status ${response.status}`);
  }

  const text = await response.text();
  return text;
}


async function main(): Promise<void> {
  const args = process.argv.slice(2);

  if (args.length < 2) {
    console.error("Error: Hash value is required.");
    console.error("Usage: npx ts-node check.ts <hash_value> <skill_md_path> [url]");
    process.exit(2);
  }

  const targetHash = args[0];
  const skillMdPath = args[1];
  const url = args[2] || "";

  let skillContent = "";
  if (skillMdPath) {
    try {
      skillContent = readFileSync(skillMdPath, "utf-8");
    } catch (e) {
      console.error(`[Skill Scope] Failed to read SKILL.md: ${e}`);
      skillContent = "";
    }
  }

  console.log(`[Skill Scope] Analyzing hash: ${targetHash}`);

  let responseText = "";
  try {
    responseText = await callAsApi(targetHash, skillContent, url);
  } catch (e) {
    console.error(`[Skill Scope] Failed to call API: ${e}`);
    process.exit(3);
  }

  try {
    const result = JSON.parse(responseText);
    const data = result.data as Record<string, unknown>;
    const securityResult = (data?.securityResult as string) || "";

    if (securityResult === "ACCEPT") {
      console.log(
        "[Skill Scope] Benign: Scan completed, verification passed."
      );
      process.exit(0);
    } else if (securityResult === "REJECT") {
      console.error(
        "[Skill Scope] Malicious: Malicious Skill detected! This skill poses a serious security threat."
      );
      process.exit(1);
    } else {
      console.error(`[Skill Scope] Unknown security result`);
      process.exit(2);
    }
  } catch (e) {
    console.error(`[Skill Scope] Failed to parse response: ${e}`);
    process.exit(3);
  }
}

main();