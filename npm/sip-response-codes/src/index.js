"use strict";

const codes = require("./codes");

/** All codes, frozen dataset: { [code]: { code, name, class, retryable, rfc, description } } */
module.exports.codes = codes;

/**
 * Get the metadata for a SIP response code.
 * @param {number|string} code
 * @returns {object|null} frozen entry, or null if the code is unknown
 */
function getCode(code) {
  const n = Number(code);
  if (!Number.isInteger(n)) return null;
  return codes[n] || null;
}
module.exports.getCode = getCode;

/**
 * Get the class of a SIP code: provisional, success, redirection, client_error, server_error, global_error, or null for unknown.
 * @param {number|string} code
 * @returns {string|null}
 */
function getClass(code) {
  const entry = getCode(code);
  return entry ? entry.class : null;
}
module.exports.getClass = getClass;

/** True if the code is a 1xx provisional response. */
module.exports.isProvisional = function (code) {
  return getClass(code) === "provisional";
};

/** True if the code is a 2xx success response. */
module.exports.isSuccess = function (code) {
  return getClass(code) === "success";
};

/** True if the code is a 3xx redirection response. */
module.exports.isRedirect = function (code) {
  return getClass(code) === "redirection";
};

/** True if the code is any error class (4xx, 5xx, or 6xx). */
module.exports.isError = function (code) {
  const c = getClass(code);
  return c === "client_error" || c === "server_error" || c === "global_error";
};

/** True if the code is a 4xx client error. */
module.exports.isClientError = function (code) {
  return getClass(code) === "client_error";
};

/** True if the code is a 5xx server error. */
module.exports.isServerError = function (code) {
  return getClass(code) === "server_error";
};

/** True if the code is a 6xx global error. */
module.exports.isGlobalError = function (code) {
  return getClass(code) === "global_error";
};

/**
 * True if the code is flagged as retryable per our dataset.
 * Retry semantics vary by code — always consult the RFC linked in the entry for the exact behavior.
 */
module.exports.isRetryable = function (code) {
  const entry = getCode(code);
  return entry ? entry.retryable === true : false;
};

/**
 * Return every code whose class matches.
 * @param {string} className provisional | success | redirection | client_error | server_error | global_error
 * @returns {object[]} array of frozen entries
 */
module.exports.byClass = function (className) {
  return Object.values(codes).filter(function (entry) { return entry.class === className; });
};

/** Array of all numeric codes in ascending order. */
module.exports.allCodes = Object.keys(codes).map(Number).sort(function (a, b) { return a - b; });

/** Array of all entries. */
module.exports.allEntries = Object.values(codes);
