import { useState, useEffect, useRef } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Mic, Circle, Check, X, Pause, Play, ArrowLeft } from "lucide-react";
import { useFinancialContext } from "@/hooks/useFinancialContext";

export default function AINegotiationCoachPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get("session");
  const financialContext = useFinancialContext();

  {/* TODO: pass sessionId & config to coaching runtime */}

  // Interactive state for checkboxes
  const [checklist, setChecklist] = useState([
    { id: 1, text: "Draft counteroffer email for approval", checked: false },
    { id: 2, text: "Ask for payment term discount if prepayment requested", checked: false },
    { id: 3, text: "Escalate to CPO if they won't go below +8%", checked: false },
  ]);

  const toggleCheckbox = (id: number) => {
    setChecklist(prev => 
      prev.map(item => item.id === id ? { ...item, checked: !item.checked } : item)
    );
  };

  // Floating coach state (primarily for mobile)
  const [showFloatingCoach, setShowFloatingCoach] = useState(false);
  const [isListening, setIsListening] = useState(true);
  const callWindowRef = useRef<HTMLDivElement>(null);

  // {/* TODO: responsive logic for when to show PiP */}
  // Show mini-player when call window scrolls out of view (mainly on mobile)
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        // Show floating coach when call window is NOT visible AND on mobile
        const isMobile = window.innerWidth < 1280; // xl breakpoint
        setShowFloatingCoach(!entry.isIntersecting && isMobile);
      },
      {
        threshold: 0.1,
      }
    );

    if (callWindowRef.current) {
      observer.observe(callWindowRef.current);
    }

    return () => {
      if (callWindowRef.current) {
        observer.unobserve(callWindowRef.current);
      }
    };
  }, []);

  return (
    <div className="min-h-screen bg-background">
      {/* Two-Panel Layout */}
      <div className="flex flex-col xl:flex-row w-full h-screen">
        
        {/* LEFT PANEL - Fixed Call Window (always visible on desktop) */}
        <div 
          ref={callWindowRef}
          className="xl:w-[70%] xl:min-w-[700px] xl:sticky xl:top-0 xl:self-start xl:h-screen xl:overflow-hidden bg-white border-r border-border flex flex-col"
        >
          <div className="p-6 flex flex-col justify-between flex-1">
            
            {/* Header Content */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <button
                    onClick={() => navigate(sessionId ? `/setup?session=${sessionId}` : "/setup")}
                    className="p-2 hover:bg-muted rounded-lg transition-colors"
                    aria-label="Back to Setup"
                  >
                    <ArrowLeft className="h-5 w-5" />
                  </button>
                  <div>
                    <h1 className="text-2xl font-semibold tracking-tight text-foreground">
                      AI Negotiation Coach
                    </h1>
                    <p className="text-sm text-muted-foreground">
                      Real-time guidance during supplier conversations.
                    </p>
                  </div>
                </div>
                <div className="inline-flex items-center px-3 py-1.5 rounded-full bg-amber-50 border border-amber-200">
                  <span className="text-sm font-medium text-amber-700">Pilot Mode</span>
                </div>
              </div>
            </div>

            {/* Large Avatar / Video Window */}
            <div className="relative rounded-xl overflow-hidden bg-gradient-avatar aspect-video flex items-center justify-center border border-border shadow-lg">
              {/* TODO: Embed Beyond Presence avatar iframe/player here */}
              <div className="text-center space-y-4 px-6">
                <div className="relative w-20 h-20 mx-auto">
                  <div className="absolute inset-0 rounded-full bg-primary/20 animate-pulse" />
                  <div className="absolute inset-3 rounded-full bg-primary/30 animate-pulse" style={{ animationDelay: '150ms' }} />
                  <div className="absolute inset-6 rounded-full bg-primary/50" />
                </div>
                <p className="text-white/90 font-medium text-lg">
                  AI Coach Avatar Stream — Beyond Presence
                </p>
              </div>
            </div>

            {/* Bottom spacer */}
            <div></div>

          </div>
        </div>

        {/* RIGHT PANEL - Scrollable Notes / Intelligence Dashboard */}
        <div className="flex-1 xl:w-[30%] overflow-y-auto bg-background">
          <div className="p-6 space-y-6">
            
            {/* Current Call Context */}
            <div className="bg-white rounded-xl border border-border shadow-sm p-6">
              <h3 className="text-lg font-semibold text-foreground mb-4">Current Call Context</h3>
              {/* TODO: populate from scenario metadata */}
              <div className="space-y-3">
                <div className="flex justify-between items-start gap-4">
                  <span className="text-sm font-medium text-muted-foreground">Supplier:</span>
                  <span className="text-sm text-foreground text-right">ACME Steel GmbH</span>
                </div>
                <div className="flex justify-between items-start gap-4">
                  <span className="text-sm font-medium text-muted-foreground">Topic:</span>
                  <span className="text-sm text-foreground text-right">Raw material price increase</span>
                </div>
                <div className="flex justify-between items-start gap-4">
                  <span className="text-sm font-medium text-muted-foreground">Your target:</span>
                  <span className="text-sm text-primary font-medium text-right">{financialContext.formatPercentage(financialContext.targetCounter - financialContext.supplierAsk)} vs. their ask</span>
                </div>
              </div>
            </div>

            {/* Live Transcript */}
            <div className="bg-white rounded-xl border border-border shadow-sm p-6">
              <h3 className="text-lg font-semibold text-foreground mb-4">Live Transcript</h3>
              {/* TODO: Live ASR transcript injection */}
              <div className="h-64 overflow-y-auto bg-gray-50 rounded-lg p-4 text-sm leading-relaxed space-y-3 border border-border">
                <div>
                  <span className="font-medium text-foreground">Supplier:</span>
                  <span className="text-muted-foreground"> We're seeing +15% cost due to nickel and energy.</span>
                </div>
                <div>
                  <span className="font-medium text-foreground">You:</span>
                  <span className="text-muted-foreground"> 15% feels high. Help me understand the breakdown?</span>
                </div>
                <div className="bg-primary/10 rounded-lg px-3 py-2">
                  <span className="font-medium text-primary">Coach Insight:</span>
                  <span className="text-foreground"> Market index for nickel is only up ~7–9%. High bluff likelihood.</span>
                </div>
                <div>
                  <span className="font-medium text-foreground">Supplier:</span>
                  <span className="text-muted-foreground"> Our procurement costs are up across the board. Transportation alone is +20%.</span>
                </div>
                <div>
                  <span className="font-medium text-foreground">You:</span>
                  <span className="text-muted-foreground"> I understand the pressure, but I need to see data. Can you share the cost breakdown?</span>
                </div>
                <div className="bg-primary/10 rounded-lg px-3 py-2">
                  <span className="font-medium text-primary">Coach Insight:</span>
                  <span className="text-foreground"> Good move. Asking for transparency puts pressure on them to justify the ask.</span>
                </div>
              </div>
            </div>

            {/* Financial Impact */}
            <div className="bg-white rounded-xl border border-border shadow-sm p-6">
              <h3 className="text-lg font-semibold text-foreground mb-4">Financial Impact</h3>
              {/* TODO: compute from mapped CSV data */}
              <div className="space-y-3">
                <div className="flex justify-between items-start gap-4">
                  <span className="text-sm font-medium text-muted-foreground">Annual spend at current price:</span>
                  <span className="text-sm text-foreground font-semibold">{financialContext.formatCurrency(financialContext.currentSpend)}</span>
                </div>
                <div className="flex justify-between items-start gap-4">
                  <span className="text-sm font-medium text-muted-foreground">Cost impact of {financialContext.formatPercentage(financialContext.supplierAsk)} ask:</span>
                  <span className="text-sm text-destructive font-semibold">+{financialContext.formatCurrency(financialContext.costImpact)} / year</span>
                </div>
                <div className="flex justify-between items-start gap-4">
                  <span className="text-sm font-medium text-muted-foreground">Target counter:</span>
                  <span className="text-sm text-success font-semibold">{financialContext.formatPercentage(financialContext.targetCounter)} max = save ~{financialContext.formatCurrency(financialContext.potentialSavings)} / year</span>
                </div>
              </div>
              <p className="text-xs text-muted-foreground pt-3 border-t border-border mt-4">
                This estimate will be logged and surfaced to Finance.
              </p>
            </div>

            {/* Next Steps */}
            <div className="bg-white rounded-xl border border-border shadow-sm p-6">
              <h3 className="text-lg font-semibold text-foreground mb-4">Next Steps</h3>
              <div className="space-y-3">
                {checklist.map((item) => (
                  <label 
                    key={item.id}
                    className="flex items-start gap-3 cursor-pointer group"
                    onClick={() => toggleCheckbox(item.id)}
                  >
                    <div className={`mt-0.5 w-4 h-4 rounded border-2 flex items-center justify-center transition-all ${
                      item.checked 
                        ? 'bg-primary border-primary' 
                        : 'border-muted-foreground/40 group-hover:border-primary/50'
                    }`}>
                      {item.checked && <Check className="h-3 w-3 text-white" />}
                    </div>
                    <span className={`text-sm flex-1 ${
                      item.checked ? 'text-muted-foreground line-through' : 'text-foreground'
                    }`}>
                      {item.text}
                    </span>
                  </label>
                ))}
              </div>
              <div className="pt-4 space-y-2 border-t border-border mt-4">
                {/* TODO: escalation brief generator */}
                <button className="w-full px-4 py-3 rounded-lg bg-gradient-hero text-white font-medium hover:shadow-glow-sm transition-all duration-200 hover:scale-[1.02] cursor-pointer">
                  Generate escalation brief
                </button>
                <p className="text-xs text-muted-foreground text-center">
                  Creates a summary for leadership with risk, numbers, and ask.
                </p>
              </div>
            </div>

            {/* Supplier History & Commitments */}
            <div className="bg-white rounded-xl border border-border shadow-sm p-6">
              <h3 className="text-lg font-semibold text-foreground mb-4">Supplier History & Commitments</h3>
              {/* TODO: pull from supplier record / ERP */}
              <div className="space-y-3 text-sm">
                <div className="flex gap-3">
                  <span className="text-muted-foreground font-medium whitespace-nowrap">Jul 2025 —</span>
                  <span className="text-foreground">Agreed to freeze logistics surcharge until Jan 2026.</span>
                </div>
                <div className="flex gap-3">
                  <span className="text-muted-foreground font-medium whitespace-nowrap">May 2025 —</span>
                  <span className="text-foreground">Late delivery on Line 3 caused 48h downtime. Escalation to COO.</span>
                </div>
                <div className="flex gap-3">
                  <span className="text-muted-foreground font-medium whitespace-nowrap">Feb 2025 —</span>
                  <span className="text-foreground">Committed to 45-day payment terms in exchange for guaranteed volume.</span>
                </div>
              </div>
              
              <div className="pt-4 border-t border-border mt-4 space-y-3">
                <h4 className="text-base font-semibold text-foreground">Open Commitments</h4>
                <div className="space-y-3">
                  <div className="flex items-start justify-between gap-4">
                    <span className="text-sm text-foreground flex-1">
                      Supplier to provide revised lead time forecast by Oct 28
                    </span>
                    <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-amber-50 text-amber-700 border border-amber-200 whitespace-nowrap">
                      Pending
                    </span>
                  </div>
                  <div className="flex items-start justify-between gap-4">
                    <span className="text-sm text-foreground flex-1">
                      We to review exclusivity clause with Legal
                    </span>
                    <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-blue-50 text-blue-700 border border-blue-200 whitespace-nowrap">
                      In review
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Compliance & Risk */}
            <div className="bg-white rounded-xl border border-border shadow-sm p-6">
              <h3 className="text-lg font-semibold text-foreground mb-4">Compliance & Risk</h3>
              {/* TODO: policy engine hooks */}
              <div className="space-y-3">
                <div className="flex items-start justify-between gap-4 p-4 rounded-lg bg-amber-50 border border-amber-200">
                  <div className="flex-1">
                    <div className="font-medium text-sm text-foreground">Payment Terms</div>
                    <div className="text-sm text-muted-foreground mt-1">
                      Request for prepayment detected. Requires CFO approval above €250k.
                    </div>
                  </div>
                  <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-amber-100 text-amber-800 border border-amber-300 whitespace-nowrap">
                    Action needed
                  </span>
                </div>
                
                <div className="flex items-start justify-between gap-4 p-4 rounded-lg bg-blue-50 border border-blue-200">
                  <div className="flex-1">
                    <div className="font-medium text-sm text-foreground">Exclusivity Language</div>
                    <div className="text-sm text-muted-foreground mt-1">
                      Exclusive supply request mentioned. Legal review required before agreeing.
                    </div>
                  </div>
                  <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 border border-blue-300 whitespace-nowrap">
                    Watch
                  </span>
                </div>
                
                <div className="flex items-start justify-between gap-4 p-4 rounded-lg bg-amber-50 border border-amber-200">
                  <div className="flex-1">
                    <div className="font-medium text-sm text-foreground">Sustainability / ESG</div>
                    <div className="text-sm text-muted-foreground mt-1">
                      No current CO2 reporting on file for this supplier in 2025. Flag for ESG team.
                    </div>
                  </div>
                  <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-amber-100 text-amber-800 border border-amber-300 whitespace-nowrap">
                    Action needed
                  </span>
                </div>
              </div>
            </div>

            {/* Executive Impact */}
            <div className="bg-white rounded-xl border border-border shadow-sm p-6">
              <h3 className="text-lg font-semibold text-foreground mb-4">Executive Impact</h3>
              {/* TODO: auto-generate CFO/CPO briefing */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
                <div className="border border-border rounded-lg p-4 bg-background">
                  <div className="text-xs text-muted-foreground mb-1">Savings vs Supplier Ask</div>
                  <div className="text-lg font-semibold text-foreground">{financialContext.formatCurrency(financialContext.potentialSavings)} / year</div>
                </div>
                <div className="border border-border rounded-lg p-4 bg-background">
                  <div className="text-xs text-muted-foreground mb-1">Risk Exposure</div>
                  <div className="text-lg font-semibold text-destructive">{financialContext.riskExposure} (supply continuity mentioned)</div>
                </div>
                <div className="border border-border rounded-lg p-4 bg-background">
                  <div className="text-xs text-muted-foreground mb-1">Leverage Position</div>
                  <div className="text-lg font-semibold text-success">{financialContext.leveragePosition} — we're 18% of their total volume</div>
                </div>
                <div className="border border-border rounded-lg p-4 bg-background">
                  <div className="text-xs text-muted-foreground mb-1">Next Escalation Owner</div>
                  <div className="text-lg font-semibold text-foreground">{financialContext.nextEscalationOwner}</div>
                </div>
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed border-t border-border pt-4">
                This negotiation is financially material. If we accept {financialContext.formatPercentage(financialContext.supplierAsk)}, cost impact is ~{financialContext.formatCurrency(financialContext.costImpact)}/year. Coach recommends holding at {financialContext.formatPercentage(financialContext.targetCounter)} cap and escalating if they won't move.
              </p>
            </div>

            {/* Post-Session Feedback (Placeholder / Future) */}
            <div className="bg-white rounded-xl border border-border shadow-sm p-6">
              <h3 className="text-lg font-semibold text-foreground mb-4">Coaching Summary</h3>
              {/* TODO: generate performance scoring */}
              <div className="space-y-3 text-sm">
                <div className="flex gap-3">
                  <span className="text-success">✓</span>
                  <span className="text-foreground">You held price pressure well.</span>
                </div>
                <div className="flex gap-3">
                  <span className="text-amber-600">⚠</span>
                  <span className="text-foreground">You conceded payment terms too early without getting anything in return.</span>
                </div>
                <div className="flex gap-3">
                  <span className="text-primary">→</span>
                  <span className="text-foreground">Next improvement: ask for volume commitment first.</span>
                </div>
              </div>
              <div className="mt-4 pt-4 border-t border-border">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-muted-foreground">Margin Defense:</span>
                  <span className="text-lg font-semibold text-primary">8/10</span>
                </div>
              </div>
            </div>

          </div>
        </div>
      </div>

      {/* Floating Mini-Player (Picture-in-Picture) - primarily for mobile */}
      {showFloatingCoach && (
        <div className="fixed bottom-4 right-4 xl:hidden z-50 w-60 bg-white rounded-xl border border-border shadow-2xl overflow-hidden">
          <div className="relative">
            {/* Close button */}
            <button
              onClick={() => setShowFloatingCoach(false)}
              className="absolute top-2 right-2 z-10 p-1 bg-black/20 hover:bg-black/40 rounded-full transition-colors"
              aria-label="Close mini player"
            >
              <X className="h-4 w-4 text-white" />
            </button>

            {/* Status indicator */}
            <div className="absolute top-2 left-2 z-10 flex items-center gap-1.5 bg-black/20 backdrop-blur-sm rounded-full px-2.5 py-1">
              <Circle className={`h-2 w-2 ${isListening ? 'fill-success text-success' : 'fill-muted-foreground text-muted-foreground'} animate-pulse`} />
              <span className="text-xs font-medium text-white">
                {isListening ? 'Listening' : 'Paused'}
              </span>
            </div>

            {/* Mini avatar window */}
            <div className="relative aspect-video bg-gradient-avatar flex items-center justify-center">
              {/* TODO: Embed Beyond Presence avatar iframe/player (mini view) */}
              <div className="text-center space-y-2 px-4">
                <div className="relative w-12 h-12 mx-auto">
                  <div className="absolute inset-0 rounded-full bg-primary/20 animate-pulse" />
                  <div className="absolute inset-2 rounded-full bg-primary/30 animate-pulse" style={{ animationDelay: '150ms' }} />
                  <div className="absolute inset-4 rounded-full bg-primary/50" />
                </div>
                <p className="text-white/90 font-medium text-xs">
                  AI Coach Avatar Stream — Beyond Presence
                </p>
              </div>
            </div>

            {/* Controls */}
            <div className="p-3 space-y-2 bg-white">
              <div className="flex items-center gap-2">
                <button 
                  className="h-10 w-10 rounded-full bg-gradient-hero flex items-center justify-center shadow-glow-sm hover:shadow-glow transition-all cursor-pointer flex-shrink-0"
                  aria-label="Speak to coach"
                >
                  <Mic className="h-4 w-4 text-white" />
                </button>
                <button
                  onClick={() => setIsListening(!isListening)}
                  className="flex-1 px-3 py-2 rounded-lg border border-border bg-white hover:bg-gray-50 text-xs font-medium text-foreground transition-colors cursor-pointer flex items-center justify-center gap-1.5"
                  aria-label={isListening ? "Pause listening" : "Resume listening"}
                >
                  {isListening ? (
                    <>
                      <Pause className="h-3 w-3" />
                      <span>Pause</span>
                    </>
                  ) : (
                    <>
                      <Play className="h-3 w-3" />
                      <span>Resume</span>
                    </>
                  )}
                </button>
              </div>
              <p className="text-xs text-muted-foreground text-center leading-tight">
                Hold mic and speak. The coach will answer in real time.
              </p>
              <p className="text-xs text-muted-foreground/70 italic text-center">
                You can pause listening at any time.
              </p>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
