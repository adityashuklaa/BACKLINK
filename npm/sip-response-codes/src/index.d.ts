export type SipResponseClass =
  | "provisional"
  | "success"
  | "redirection"
  | "client_error"
  | "server_error"
  | "global_error";

export interface SipResponseCode {
  /** Numeric status code (e.g. 200, 486, 603). */
  readonly code: number;
  /** Short canonical name (e.g. "OK", "Busy Here", "Decline"). */
  readonly name: string;
  /** Class grouping of the code. */
  readonly class: SipResponseClass;
  /** Whether the code is typically retryable. Consult the linked RFC for exact semantics. */
  readonly retryable: boolean;
  /** RFC reference that defines the code. */
  readonly rfc: string;
  /** Human-readable description. */
  readonly description: string;
}

/** Frozen map of every code number to its entry. */
export const codes: Readonly<Record<number, SipResponseCode>>;

/** Look up a code. Returns null for unknown codes. */
export function getCode(code: number | string): SipResponseCode | null;

/** Get the class name for a code, or null for unknown codes. */
export function getClass(code: number | string): SipResponseClass | null;

export function isProvisional(code: number | string): boolean;
export function isSuccess(code: number | string): boolean;
export function isRedirect(code: number | string): boolean;
export function isError(code: number | string): boolean;
export function isClientError(code: number | string): boolean;
export function isServerError(code: number | string): boolean;
export function isGlobalError(code: number | string): boolean;
export function isRetryable(code: number | string): boolean;

/** Every entry whose class matches. */
export function byClass(className: SipResponseClass): SipResponseCode[];

/** All numeric codes, ascending. */
export const allCodes: readonly number[];

/** All entries. */
export const allEntries: readonly SipResponseCode[];
