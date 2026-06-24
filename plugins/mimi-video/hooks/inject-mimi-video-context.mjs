#!/usr/bin/env node

import { readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const pluginRoot = process.env.CODESHELL_PLUGIN_ROOT || resolve(scriptDir, "..");

function readStdin() {
  return new Promise((resolvePromise) => {
    let data = "";
    process.stdin.setEncoding("utf8");
    process.stdin.on("data", (chunk) => {
      data += chunk;
    });
    process.stdin.on("end", () => resolvePromise(data));
    process.stdin.on("error", () => resolvePromise(""));
  });
}

function safeJson(raw) {
  try {
    return JSON.parse(raw);
  } catch {
    return {};
  }
}

function emitContext() {
  const skillPath = join(pluginRoot, "skills", "using-mimi-video", "SKILL.md");
  let skill;
  try {
    skill = readFileSync(skillPath, "utf8");
  } catch {
    return;
  }

  const context = [
    "<EXTREMELY_IMPORTANT>",
    "You have mimi-video producer workflow support.",
    "",
    `Plugin root: ${pluginRoot}`,
    "",
    "Below is the full content of the mimi-video bootstrap skill (using-mimi-video). When the user wants to create, initialize, continue, review, or revise an AI short-drama/video workflow, follow it. For the other mimi-video skills, use the Skill tool.",
    "",
    skill,
    "</EXTREMELY_IMPORTANT>",
  ].join("\n");

  process.stdout.write(JSON.stringify({ additionalContext: context }));
}

const raw = await readStdin();
const ctx = safeJson(raw);
const data = ctx && typeof ctx === "object" && ctx.data && typeof ctx.data === "object" ? ctx.data : {};

if (data.isSubAgent === true) process.exit(0);

const event = process.env.CODESHELL_HOOK_EVENT || ctx.eventName || "";

// SessionStart-only, injected unconditionally (no project detection): the skill
// covers initializing a brand-new mimi-video project from an empty directory, so
// gating on "looks like a mimi project" would break the cold-start/init case.
// Users who don't want it disable the plugin. Subagents are skipped above.
if (event === "on_session_start") {
  emitContext();
}
