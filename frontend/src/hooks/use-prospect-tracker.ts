"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { usePathname } from "next/navigation";
import { leadService } from "@/services/lead-service";
import { SignalType } from "@/types/lead";

const SESSION_STORAGE_KEY = "ps21_session_id";
const PROSPECT_STORAGE_KEY = "ps21_prospect_id";

function generateSessionId(): string {
  const randomPart = Math.random().toString(36).substring(2, 15);
  const timePart = Date.now().toString(36);
  return `sess_${timePart}_${randomPart}`;
}

export function useProspectTracker(autoTrackPageView = true) {
  const pathname = usePathname();
  const [sessionId, setSessionId] = useState<string>("");
  const [prospectId, setProspectIdState] = useState<string | null>(null);

  const enterTimeRef = useRef<number>(0);
  const sessionIdRef = useRef<string>("");
  const prospectIdRef = useRef<string | null>(null);

  // Initialize session ID and prospect ID asynchronously / on mount
  useEffect(() => {
    let storedSession = "";
    let storedProspect: string | null = null;

    try {
      storedSession = localStorage.getItem(SESSION_STORAGE_KEY) || "";
      if (!storedSession) {
        storedSession = generateSessionId();
        localStorage.setItem(SESSION_STORAGE_KEY, storedSession);
      }
      storedProspect = localStorage.getItem(PROSPECT_STORAGE_KEY);
    } catch {
      // Storage unavailable fallback
      storedSession = generateSessionId();
    }

    sessionIdRef.current = storedSession;
    prospectIdRef.current = storedProspect;
    enterTimeRef.current = Date.now();

    // Defer state update slightly to prevent synchronous cascading render warning
    const timer = setTimeout(() => {
      setSessionId(storedSession);
      if (storedProspect) {
        setProspectIdState(storedProspect);
      }
    }, 0);

    return () => clearTimeout(timer);
  }, []);

  const setProspectId = useCallback((id: string) => {
    try {
      localStorage.setItem(PROSPECT_STORAGE_KEY, id);
    } catch {
      // Ignore
    }
    setProspectIdState(id);
    prospectIdRef.current = id;
  }, []);

  // Generic signal tracking function
  const trackSignal = useCallback(
    async (signalType: SignalType, payload: Record<string, unknown> = {}) => {
      const activeSession = sessionIdRef.current || sessionId;
      if (!activeSession) return;

      try {
        await leadService.recordSignal({
          session_id: activeSession,
          prospect_id: prospectIdRef.current || prospectId || undefined,
          signal_type: signalType,
          payload: {
            ...payload,
            pathname: typeof window !== "undefined" ? window.location.pathname : "",
            referrer: typeof document !== "undefined" ? document.referrer : "",
          },
          client_timestamp: new Date().toISOString(),
        });
      } catch (err) {
        console.debug("Signal track failed:", err);
      }
    },
    [sessionId, prospectId]
  );

  // Track page view and calculate dwell time
  useEffect(() => {
    if (!autoTrackPageView || !sessionId) return;

    enterTimeRef.current = Date.now();

    // Emit page_view
    trackSignal("page_view", {
      path: pathname,
      title: typeof document !== "undefined" ? document.title : "",
    });

    const sendDwellTime = () => {
      const dwellSeconds = Math.round((Date.now() - enterTimeRef.current) / 1000);
      if (dwellSeconds >= 3) {
        trackSignal("time_on_page", {
          path: pathname,
          duration_seconds: dwellSeconds,
        });
      }
    };

    const handleVisibilityChange = () => {
      if (document.visibilityState === "hidden") {
        sendDwellTime();
      } else {
        enterTimeRef.current = Date.now();
      }
    };

    window.addEventListener("beforeunload", sendDwellTime);
    document.addEventListener("visibilitychange", handleVisibilityChange);

    return () => {
      sendDwellTime();
      window.removeEventListener("beforeunload", sendDwellTime);
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, [pathname, sessionId, autoTrackPageView, trackSignal]);

  // Convenience helper methods
  const trackQuoteAttempt = useCallback(
    (payload: Record<string, unknown>) => trackSignal("quote_attempt", payload),
    [trackSignal]
  );

  const trackCalculatorUsed = useCallback(
    (payload: Record<string, unknown>) => trackSignal("coverage_calculator_used", payload),
    [trackSignal]
  );

  const trackComparisonViewed = useCallback(
    (payload: Record<string, unknown>) => trackSignal("comparison_viewed", payload),
    [trackSignal]
  );

  const trackFaqOpened = useCallback(
    (faqQuestion: string) => trackSignal("faq_opened", { question: faqQuestion }),
    [trackSignal]
  );

  const trackDropOffStep = useCallback(
    (stepName: string, payload: Record<string, unknown> = {}) =>
      trackSignal("drop_off_step", { step: stepName, ...payload }),
    [trackSignal]
  );

  const trackChatInitiated = useCallback(
    (payload: Record<string, unknown> = {}) => trackSignal("chat_initiated", payload),
    [trackSignal]
  );

  return {
    sessionId,
    prospectId,
    setProspectId,
    trackSignal,
    trackQuoteAttempt,
    trackCalculatorUsed,
    trackComparisonViewed,
    trackFaqOpened,
    trackDropOffStep,
    trackChatInitiated,
  };
}
