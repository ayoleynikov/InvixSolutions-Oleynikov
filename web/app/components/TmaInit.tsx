"use client";

import { useEffect } from "react";

declare global {
  interface Window {
    Telegram?: {
      WebApp?: {
        ready: () => void;
        expand: () => void;
        setHeaderColor?: (color: string) => void;
      };
    };
  }
}

export function TmaInit() {
  useEffect(() => {
    const tg = window.Telegram?.WebApp;
    if (!tg) {
      return;
    }
    tg.ready();
    tg.expand();
    tg.setHeaderColor?.("#ffffff");
  }, []);

  return null;
}
