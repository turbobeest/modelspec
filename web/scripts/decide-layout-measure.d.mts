import type { Page } from "@playwright/test";

export interface CheckRow { check: string; pass: boolean; detail: string }
export interface CounterView { text: string; summary: string; bottom: number; viewport: number }

export const GUTTER: number;
export const GAP: number;
export function routeFixtures(page: Page): Promise<void>;
export function openDecide(page: Page, base?: string): Promise<void>;
export function measure(page: Page): Promise<unknown>;
export function check(layout: unknown): CheckRow[];
export function counterView(page: Page): Promise<CounterView | null>;
