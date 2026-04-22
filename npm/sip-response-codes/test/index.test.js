"use strict";
// Hand-rolled tests (no dependencies). Run: node test/index.test.js

const lib = require("../src/index");
const assert = require("assert");

let passed = 0;
let failed = 0;
const t = (name, fn) => {
  try { fn(); console.log("  ok  " + name); passed++; }
  catch (e) { console.log("  FAIL " + name + ": " + e.message); failed++; }
};

console.log("sip-response-codes tests");

t("codes is frozen and contains 200 OK", () => {
  assert.strictEqual(lib.codes[200].name, "OK");
  assert.strictEqual(Object.isFrozen(lib.codes), true);
});

t("getCode returns entry for known codes", () => {
  const entry = lib.getCode(486);
  assert.strictEqual(entry.name, "Busy Here");
  assert.strictEqual(entry.class, "client_error");
  assert.strictEqual(entry.retryable, true);
});

t("getCode returns null for unknown code", () => {
  assert.strictEqual(lib.getCode(999), null);
  assert.strictEqual(lib.getCode("abc"), null);
  assert.strictEqual(lib.getCode(null), null);
});

t("getCode accepts string input", () => {
  assert.strictEqual(lib.getCode("200").name, "OK");
});

t("class predicates work correctly", () => {
  assert.strictEqual(lib.isProvisional(180), true);
  assert.strictEqual(lib.isProvisional(200), false);
  assert.strictEqual(lib.isSuccess(200), true);
  assert.strictEqual(lib.isSuccess(202), true);
  assert.strictEqual(lib.isRedirect(302), true);
  assert.strictEqual(lib.isClientError(404), true);
  assert.strictEqual(lib.isServerError(500), true);
  assert.strictEqual(lib.isGlobalError(603), true);
  assert.strictEqual(lib.isError(404), true);
  assert.strictEqual(lib.isError(500), true);
  assert.strictEqual(lib.isError(603), true);
  assert.strictEqual(lib.isError(200), false);
});

t("isRetryable matches dataset", () => {
  assert.strictEqual(lib.isRetryable(401), true);
  assert.strictEqual(lib.isRetryable(403), false);
  assert.strictEqual(lib.isRetryable(480), true);
  assert.strictEqual(lib.isRetryable(603), false);
  assert.strictEqual(lib.isRetryable(999), false);
});

t("byClass returns correct counts", () => {
  assert.ok(lib.byClass("provisional").length >= 5);
  assert.ok(lib.byClass("success").length >= 2);
  assert.ok(lib.byClass("client_error").length >= 20);
  assert.ok(lib.byClass("server_error").length >= 7);
  assert.ok(lib.byClass("global_error").length >= 5);
});

t("allCodes is sorted ascending", () => {
  const c = lib.allCodes;
  for (let i = 1; i < c.length; i++) assert.ok(c[i] > c[i-1], "not sorted at " + i);
  assert.ok(c.length >= 60, "expected at least 60 codes, got " + c.length);
});

t("every entry has required fields", () => {
  for (const e of lib.allEntries) {
    assert.ok(Number.isInteger(e.code), "code not integer: " + JSON.stringify(e));
    assert.ok(typeof e.name === "string" && e.name.length > 0, "bad name: " + e.code);
    assert.ok(["provisional","success","redirection","client_error","server_error","global_error"].includes(e.class), "bad class: " + e.code);
    assert.ok(typeof e.retryable === "boolean", "bad retryable: " + e.code);
    assert.ok(typeof e.rfc === "string" && e.rfc.startsWith("RFC"), "bad rfc: " + e.code);
    assert.ok(typeof e.description === "string" && e.description.length > 10, "bad desc: " + e.code);
  }
});

t("getClass is consistent with predicates", () => {
  for (const e of lib.allEntries) {
    assert.strictEqual(lib.getClass(e.code), e.class);
  }
});

console.log("\n" + passed + " passed, " + failed + " failed");
process.exit(failed > 0 ? 1 : 0);
