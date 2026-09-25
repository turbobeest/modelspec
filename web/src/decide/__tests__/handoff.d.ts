// The handoff's reference engine, plain JS, aliased in vitest.config.ts.
declare module "@handoff/modelspec-data" {
  /* eslint-disable @typescript-eslint/no-explicit-any */
  export const buildCatalogue: () => any;
  export const evaluate: (D: any, spec: any, opt?: any) => any;
  export const suggestions: (D: any, spec: any, dismissed: string[]) => any[];
  export const parseTask: (text: string) => any;
  export const relaxValue: (c: any, m: any, o: any, spec: any) => any;
  export const TEMPLATES: any[];
  export const FACETS: any[];
}
