"use client";

import * as React from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import {
  Send,
  Bot,
  User,
  Sparkles,
  AlertCircle,
  RefreshCw,
  ShieldCheck,
  SlidersHorizontal,
  ArrowRight,
  ExternalLink,
  HelpCircle,
  FileText,
} from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { CustomerAPI } from "@/services/customer-api";
import { QuoteAPI } from "@/services/quote-api";
import { ChatMessage } from "@/types/customer";
import { QuoteItem } from "@/types/quote";
import { SuggestionChips } from "@/components/customer/chat/suggestion-chips";
import { TypingIndicator } from "@/components/customer/chat/typing-indicator";
import { ResumeJourneyBanner } from "@/components/customer/chat/resume-journey-banner";
import { MarkdownRenderer } from "@/components/shared/markdown-renderer";

function CustomerChatContent() {
  const searchParams = useSearchParams();
  const productId = searchParams.get("product_id");
  const productName = searchParams.get("product_name");
  const category = searchParams.get("category");
  const action = searchParams.get("action");

  const quoteContext = React.useMemo(() => {
    if (!productId && !productName) return null;
    return {
      productId: productId || "",
      productName: productName || "Selected Plan",
      category: category || "term_life",
      action: action || "quote",
    };
  }, [productId, productName, category, action]);

  const [messages, setMessages] = React.useState<ChatMessage[]>([]);
  const [conversationId, setConversationId] = React.useState<string | undefined>(undefined);
  const [input, setInput] = React.useState("");
  const [language, setLanguage] = React.useState<"en" | "hi">("en");
  const [isLoading, setIsLoading] = React.useState(false);
  const [generatingQuote, setGeneratingQuote] = React.useState(false);
  const [suggestedChips, setSuggestedChips] = React.useState<string[]>([
    "Term Life Coverage for Family",
    "Comprehensive Health Insurance",
    "Calculate My Human Life Value",
    "Explain Room Rent Sub-limits",
  ]);
  const [resumeData, setResumeData] = React.useState<{ stage: string; lastMessage?: string | null } | null>(null);

  const scrollRef = React.useRef<HTMLDivElement>(null);
  const hasAutoPromptedRef = React.useRef(false);

  const handleSend = async (messageText: string, currentConvId?: string) => {
    const textToSend = messageText.trim();
    if (!textToSend || isLoading) return;

    const convId = currentConvId !== undefined ? currentConvId : conversationId;

    const userMsg: ChatMessage = {
      id: `temp-${Date.now()}`,
      conversation_id: convId || "current",
      sender_type: "user",
      sender_name: "You",
      content: textToSend,
      message_type: "text",
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await CustomerAPI.sendChatTurn({
        conversation_id: convId,
        message: textToSend,
        language,
      });

      setMessages((prev) => [...prev, response]);
      if (response.conversation_id) {
        setConversationId(response.conversation_id);
      }
      if (response.suggested_chips && response.suggested_chips.length > 0) {
        setSuggestedChips(response.suggested_chips);
      }
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: `err-${Date.now()}`,
        conversation_id: convId || "current",
        sender_type: "system",
        sender_name: "System Notification",
        content: err?.message || "Unable to reach advisor service. Please check your connection and try again.",
        message_type: "disclaimer",
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateQuote = async (targetProductId?: string, targetProductName?: string, targetCategory?: string) => {
    const pId = targetProductId || quoteContext?.productId;
    const pName = targetProductName || quoteContext?.productName || "Insurance Plan";
    const cat = targetCategory || quoteContext?.category || "term_life";

    if (!pId) {
      handleSend(`Could you generate an indicative quote for ${pName}?`);
      return;
    }

    setGeneratingQuote(true);
    setIsLoading(true);

    try {
      const defaultSum = cat === "term_life" ? 2500000 : 500000;
      const defaultTerm = cat === "term_life" ? 20 : 1;

      const newQuote = await QuoteAPI.createQuote({
        product_id: pId,
        sum_assured: defaultSum,
        policy_term_years: defaultTerm,
        payment_frequency: "annually",
      });

      const quoteMessage: ChatMessage = {
        id: `quote-${newQuote.id}`,
        conversation_id: conversationId || "current",
        sender_type: "agent",
        sender_name: "PS-21 Actuarial Quote Engine",
        content: `### Indicative Quote Formulated: ${newQuote.product?.name || pName}\n\nHere is your official indicative premium breakdown calculated deterministically from approved IRDAI rate tables:`,
        message_type: "quote_preview",
        widget_data: newQuote,
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, quoteMessage]);
      setSuggestedChips([
        "Customize & Recalculate Breakdown",
        "Apply for this Policy Now",
        "Explain GST & Tax Deductions",
        "Compare with other plans",
      ]);
    } catch (err: any) {
      console.error("Quote generation failed:", err);
      const errorMsg: ChatMessage = {
        id: `err-${Date.now()}`,
        conversation_id: conversationId || "current",
        sender_type: "system",
        sender_name: "Quote Engine Notice",
        content: `Could not generate quote automatically: ${err?.message || "Please ensure your customer profile is complete."}`,
        message_type: "disclaimer",
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setGeneratingQuote(false);
      setIsLoading(false);
    }
  };

  React.useEffect(() => {
    async function initChat() {
      try {
        const history = await CustomerAPI.getChatHistory();
        let currentId: string | undefined = undefined;

        if (history && history.messages && history.messages.length > 0) {
          setMessages(history.messages);
          setConversationId(history.id);
          currentId = history.id;
        } else {
          // Initial greeting
          const initialGreeting: ChatMessage = {
            id: "init-1",
            conversation_id: "init",
            sender_type: "agent",
            sender_name: "PS-21 AI Insurance Advisor",
            content:
              language === "en"
                ? "Hello! I am your certified PS-21 Insurance Advisor. I can help evaluate your protection needs, calculate your family's coverage gap, and recommend approved policies. What type of insurance are you exploring today?"
                : "नमस्ते! मैं आपका PS-21 बीमा सलाहकार हूँ। मैं आपकी सुरक्षा आवश्यकताओं का मूल्यांकन करने और उपयुक्त पॉलिसियों की सिफारिश करने में मदद कर सकता हूँ। आज आप किस प्रकार का बीमा देखना चाहते हैं?",
            message_type: "text",
            created_at: new Date().toISOString(),
          };
          setMessages([initialGreeting]);
        }

        // Check if there is an unfinished journey to resume
        const rData = await CustomerAPI.resumeJourney();
        if (rData && rData.stage !== "discovery") {
          setResumeData({
            stage: rData.stage.replace(/_/g, " "),
            lastMessage: rData.last_message,
          });
        }

        // If user came with quote intent, trigger quote workflow immediately
        if (quoteContext && !hasAutoPromptedRef.current) {
          hasAutoPromptedRef.current = true;
          setSuggestedChips([
            `Generate Indicative Quote for ${quoteContext.productName}`,
            `What are the benefits of ${quoteContext.productName}?`,
            `What are the exclusions & waiting period?`,
            `Tax benefits under Sec 80C/80D`,
          ]);

          const promptText = `I would like to get an indicative quote for ${quoteContext.productName}. Could you summarize key protections, recommended coverage limits, and estimated pricing?`;

          setTimeout(() => {
            handleSend(promptText, currentId);
          }, 350);
        } else if (searchParams.get("topic") === "hlv" && !hasAutoPromptedRef.current) {
          hasAutoPromptedRef.current = true;
          const hlvAmount = searchParams.get("amount");
          const formattedCover = hlvAmount ? `₹${Number(hlvAmount).toLocaleString("en-IN")}` : "my recommended protection";
          setSuggestedChips([
            "Why is Human Life Value important?",
            `Find plans for ${formattedCover}`,
            "How do inflation & liabilities affect my gap?",
            "What policy tenure should I choose?",
          ]);

          const promptText = `I calculated my Human Life Value (HLV) coverage requirement as ${formattedCover}. Could you explain what this means for my family's financial security and recommend matching term insurance policies?`;

          setTimeout(() => {
            handleSend(promptText, currentId);
          }, 350);
        }
      } catch (err) {
        console.error("Chat initialization error:", err);
      }
    }

    initChat();
  }, [language, quoteContext]);

  React.useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading, generatingQuote]);

  const handleChipSelect = (chip: string) => {
    if (chip.toLowerCase().includes("generate indicative quote") || chip.toLowerCase().includes("instant quote")) {
      handleGenerateQuote();
    } else if (chip === "Customize & Recalculate Breakdown") {
      window.location.assign("/customer/quotes");
    } else {
      handleSend(chip);
    }
  };

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSend(input);
  };

  return (
    <div className="space-y-4 flex flex-col h-[calc(100vh-8.5rem)]">
      <PageHeader
        title="AI Insurance Advisory Assistant"
        description="Structured need discovery, policy qualification, and instant indicative quotes."
        breadcrumbs={[
          { label: "Customer Portal", href: "/customer" },
          { label: "AI Advisor" },
        ]}
        actions={
          <div className="flex items-center gap-2">
            {/* Language Switcher */}
            <div className="flex items-center border border-slate-200 rounded-md p-0.5 bg-white shadow-2xs">
              <button
                onClick={() => setLanguage("en")}
                className={`px-2.5 py-1 text-xs rounded font-medium transition-colors ${
                  language === "en" ? "bg-blue-600 text-white" : "text-slate-600 hover:text-slate-900"
                }`}
              >
                English
              </button>
              <button
                onClick={() => setLanguage("hi")}
                className={`px-2.5 py-1 text-xs rounded font-medium transition-colors ${
                  language === "hi" ? "bg-blue-600 text-white" : "text-slate-600 hover:text-slate-900"
                }`}
              >
                हिंदी
              </button>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setMessages([]);
                setConversationId(undefined);
                hasAutoPromptedRef.current = false;
              }}
              title="Reset conversation"
            >
              <RefreshCw className="h-3.5 w-3.5 mr-1" />
              New Chat
            </Button>
          </div>
        }
      />

      {/* Compliance Advisory Alert */}
      <Alert className="py-2 border-blue-100 bg-blue-50/50 text-blue-900">
        <Sparkles className="h-4 w-4 text-blue-600" />
        <AlertTitle className="text-xs font-semibold">
          Autonomous Insurance Intelligence (Phase 5 Connected Engine)
        </AlertTitle>
        <AlertDescription className="text-[11px] text-slate-600">
          Powered by Mistral AI and LangGraph with persistent SQLite state. All rates and recommendations are indicative and subject to formal underwriting review.
        </AlertDescription>
      </Alert>

      {/* Active Quote Consultation Banner if arrived from Explore Plans */}
      {quoteContext && (
        <div className="bg-linear-to-r from-blue-50 via-indigo-50 to-blue-50 border border-blue-200 rounded-lg p-3 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shadow-2xs shrink-0">
          <div className="space-y-0.5">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="bg-blue-600 text-white text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider">
                Quote Consultation Mode
              </span>
              <span className="font-semibold text-xs text-slate-900">{quoteContext.productName}</span>
              <Badge variant="outline" className="text-[10px] capitalize bg-white text-slate-700">
                {quoteContext.category.replace(/_/g, " ")}
              </Badge>
            </div>
            <p className="text-[11px] text-slate-600">
              Evaluating actuarial rates and coverage benefits. You can ask questions below or formulate your indicative quote immediately.
            </p>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <Button
              size="sm"
              disabled={generatingQuote || isLoading}
              onClick={() => handleGenerateQuote()}
              className="text-xs bg-blue-600 hover:bg-blue-700 text-white shadow-2xs"
            >
              <Sparkles className="h-3.5 w-3.5 mr-1.5" />
              {generatingQuote ? "Calculating..." : "Instant Indicative Quote"}
            </Button>
            <Button
              size="sm"
              variant="outline"
              asChild
              className="text-xs bg-white border-blue-200 hover:bg-blue-50 text-slate-700"
            >
              <Link
                href={`/customer/quotes?product_id=${quoteContext.productId}&sum_assured=${
                  quoteContext.category === "term_life" ? 2500000 : 500000
                }&term=${quoteContext.category === "term_life" ? 20 : 1}`}
              >
                <ExternalLink className="h-3.5 w-3.5 mr-1" />
                Quotes Page
              </Link>
            </Button>
          </div>
        </div>
      )}

      {/* Main Chat Container */}
      <Card className="flex-1 flex flex-col overflow-hidden border-slate-200 bg-white shadow-2xs">
        {/* Optional Journey Resumption Prompt */}
        {resumeData && (
          <ResumeJourneyBanner
            stage={resumeData.stage}
            lastMessage={resumeData.lastMessage}
            onResume={() => {
              handleSend("I would like to resume my previous consultation.");
              setResumeData(null);
            }}
            onDismiss={() => setResumeData(null)}
          />
        )}

        {/* Scrollable Message List */}
        <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg) => {
            const isUser = msg.sender_type === "user";
            const isSystem = msg.sender_type === "system";

            if (isSystem) {
              return (
                <div key={msg.id} className="flex justify-center my-2">
                  <div className="bg-red-50 border border-red-200 text-red-700 text-xs px-3 py-1.5 rounded-md flex items-center gap-1.5">
                    <AlertCircle className="h-3.5 w-3.5" />
                    <span>{msg.content}</span>
                  </div>
                </div>
              );
            }

            return (
              <div
                key={msg.id}
                className={`flex gap-3 max-w-[85%] ${isUser ? "ml-auto flex-row-reverse" : "mr-auto"}`}
              >
                <div
                  className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-medium ${
                    isUser
                      ? "bg-blue-600 text-white"
                      : "bg-slate-100 text-slate-800 border border-slate-200"
                  }`}
                >
                  {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4 text-blue-600" />}
                </div>

                <div
                  className={`rounded-xl px-4 py-3 text-sm leading-relaxed shadow-2xs ${
                    isUser
                      ? "bg-blue-600 text-white"
                      : "bg-slate-50 text-slate-900 border border-slate-200/80"
                  }`}
                >
                  <MarkdownRenderer content={msg.content} />

                  {/* Rich Indicative Quote Preview Widget if quote was formulated */}
                  {msg.message_type === "quote_preview" && msg.widget_data && (
                    <div className="mt-3 p-3.5 rounded-xl border border-emerald-200 bg-white shadow-2xs space-y-3">
                      <div className="flex items-center justify-between border-b border-emerald-100 pb-2">
                        <div className="flex items-center gap-1.5">
                          <ShieldCheck className="h-4 w-4 text-emerald-600" />
                          <span className="font-semibold text-xs text-emerald-900">Actuarial Indicative Quote</span>
                        </div>
                        <Badge variant="outline" className="font-mono text-[10px] bg-emerald-50 text-emerald-800 border-emerald-200">
                          {msg.widget_data.quote_number}
                        </Badge>
                      </div>

                      <div className="grid grid-cols-2 gap-2 text-xs bg-slate-50 p-2.5 rounded-lg border border-slate-100">
                        <div>
                          <span className="text-[10px] text-slate-500 uppercase block font-medium">Sum Assured</span>
                          <span className="font-bold text-slate-900 text-sm">
                            ₹{Number(msg.widget_data.sum_assured).toLocaleString("en-IN")}
                          </span>
                        </div>
                        <div>
                          <span className="text-[10px] text-slate-500 uppercase block font-medium">Policy Term</span>
                          <span className="font-bold text-slate-900 text-sm">{msg.widget_data.policy_term_years} Years</span>
                        </div>
                        <div className="col-span-2 pt-2 border-t border-slate-200/60 flex justify-between items-baseline">
                          <span className="text-slate-600 font-medium">Indicative Premium:</span>
                          <span className="text-sm font-bold text-emerald-700">
                            ₹{Number(msg.widget_data.total_premium).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                            <span className="text-[10px] text-slate-500 font-normal ml-1">/{msg.widget_data.payment_frequency} (incl. GST)</span>
                          </span>
                        </div>
                      </div>

                      <div className="flex flex-wrap gap-2 pt-1">
                        <Button size="sm" asChild className="text-xs bg-blue-600 hover:bg-blue-700 text-white flex-1">
                          <Link href={`/customer/quotes/${msg.widget_data.id}`}>
                            <SlidersHorizontal className="h-3.5 w-3.5 mr-1" />
                            Customize & Breakdown
                          </Link>
                        </Button>
                        <Button size="sm" variant="outline" asChild className="text-xs border-emerald-300 text-emerald-800 hover:bg-emerald-50 flex-1">
                          <Link href={`/customer/onboarding/${msg.widget_data.id}`}>
                            Apply Now <ArrowRight className="h-3.5 w-3.5 ml-1" />
                          </Link>
                        </Button>
                      </div>
                    </div>
                  )}

                  {/* Interactive Action CTA Buttons */}
                  {msg.action_buttons && msg.action_buttons.length > 0 && (
                    <div className="mt-3 pt-2.5 border-t border-slate-200/80 flex flex-wrap gap-2">
                      {msg.action_buttons.map((btn, idx) => (
                        <Button
                          key={idx}
                          size="sm"
                          variant={btn.variant === "outline" ? "outline" : btn.variant === "secondary" ? "secondary" : "default"}
                          asChild
                          className={
                            btn.variant === "outline"
                              ? "text-xs border-slate-300 text-slate-700 hover:bg-slate-100/80"
                              : btn.variant === "secondary"
                              ? "text-xs bg-slate-100 hover:bg-slate-200 text-slate-800 border border-slate-200"
                              : "text-xs bg-blue-600 hover:bg-blue-700 text-white shadow-2xs font-medium"
                          }
                        >
                          <Link href={btn.url}>
                            {btn.label}
                            <ArrowRight className="ml-1.5 h-3.5 w-3.5" />
                          </Link>
                        </Button>
                      ))}
                    </div>
                  )}

                  <span
                    className={`mt-1.5 block text-[10px] ${
                      isUser ? "text-blue-100" : "text-slate-400"
                    }`}
                  >
                    {new Date(msg.created_at).toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </span>
                </div>
              </div>
            );
          })}

          {(isLoading || generatingQuote) && <TypingIndicator />}
        </div>

        {/* Suggested Quick-Reply Chips */}
        <SuggestionChips
          chips={suggestedChips}
          onSelect={handleChipSelect}
          disabled={isLoading || generatingQuote}
        />

        {/* Message Input Box */}
        <form onSubmit={handleFormSubmit} className="border-t border-slate-200 p-3 bg-white flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={
              language === "en"
                ? "Type your message or question about insurance terms..."
                : "अपना संदेश या बीमा संबंधी प्रश्न यहाँ लिखें..."
            }
            className="flex-1 text-sm bg-white border-slate-200"
            disabled={isLoading || generatingQuote}
          />
          <Button
            type="submit"
            size="sm"
            disabled={!input.trim() || isLoading || generatingQuote}
            className="px-4 bg-blue-600 hover:bg-blue-700 text-white"
          >
            <Send className="h-4 w-4 mr-1.5" />
            Send
          </Button>
        </form>
      </Card>
    </div>
  );
}

export default function CustomerChatPage() {
  return (
    <React.Suspense
      fallback={
        <div className="flex items-center justify-center h-64 text-xs text-slate-500">
          <RefreshCw className="h-4 w-4 animate-spin mr-2 text-blue-600" />
          Loading AI Insurance Advisor...
        </div>
      }
    >
      <CustomerChatContent />
    </React.Suspense>
  );
}
