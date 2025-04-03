import { ReactNode } from 'react';

declare global {
  namespace JSX {
    interface IntrinsicElements {
      [elemName: string]: unknown;
    }
  }
}

declare module 'react' {
  interface FunctionComponent<P = Record<string, unknown>> {
    (props: P, context?: unknown): ReactNode;
    displayName?: string;
  }
} 