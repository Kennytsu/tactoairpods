import { useState, useEffect, useRef } from "react";
import { Mic, Circle, Check, X, Pause, Play } from "lucide-react";

export default function AINegotiationCoachPage() {
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

  // Floating coach state
  const [showFloatingCoach, setShowFloatingCoach] = useState(false);
  const [isListening, setIsListening] = useState(true);
  const mainCoachRef = useRef<HTMLDivElement>(null);

  // {/* TODO: detect scroll / visibility of main coach and toggle PiP coach */}
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        // Show floating coach when main coach is NOT visible
        setShowFloatingCoach(!entry.isIntersecting);
      },
      {
        threshold: 0.1, // Trigger when 10% of element is visible
      }
    );

    if (mainCoachRef.current) {
      observer.observe(mainCoachRef.current);
    }

    return () => {
      if (mainCoachRef.current) {
        observer.unobserve(mainCoachRef.current);
      }
    };
  }, []);

  return (
    <div className="min-h-screen bg-background">
      {/* Page Header */}
      <div className="border-b border-border bg-white">
        <div className="mx-auto max-w-screen-2xl px-6 py-6">
          <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
            <div>
              <h1 className="text-3xl font-semibold tracking-tight text-foreground">
                AI Negotiation Coach
              </h1>
              <p className="mt-1 text-base text-muted-foreground">
                Real-time guidance during supplier conversations.
              </p>
            </div>
            <div className="inline-flex items-center px-3 py-1.5 rounded-full bg-amber-50 border border-amber-200">
              <span className="text-sm font-medium text-amber-700">Pilot Mode</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Container */}
      <div className="mx-auto max-w-screen-2xl p-6">
        <div className="space-y-6">
          {/* Two-column layout for main content */}
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 w-full">
            
            {/* LEFT COLUMN - Live Call */}
            <div className="bg-white rounded-xl border border-border shadow-sm p-6 space-y-6">
              
              {/* A. Coach Live Panel */}
              <div ref={mainCoachRef} className="space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-foreground">Live Coach</h2>
                  <div className="flex items-center gap-2">
                    <Circle className={`h-2.5 w-2.5 animate-pulse ${isListening ? 'fill-success text-success' : 'fill-muted-foreground text-muted-foreground'}`} />
                    <span className={`text-sm font-medium ${isListening ? 'text-success' : 'text-muted-foreground'}`}>
                      {isListening ? 'Listening' : 'Paused'}
                    </span>
                  </div>
                </div>

                {/* Avatar window */}
                <div className="relative rounded-xl overflow-hidden bg-gradient-avatar aspect-video flex items-center justify-center border border-border">
                  {/* TODO: Embed Beyond Presence avatar iframe/player here */}
                  <div className="text-center space-y-3 px-6">
                    <div className="relative w-16 h-16 mx-auto">
                      <div className="absolute inset-0 rounded-full bg-primary/20 animate-pulse" />
                      <div className="absolute inset-3 rounded-full bg-primary/30 animate-pulse" style={{ animationDelay: '150ms' }} />
                      <div className="absolute inset-6 rounded-full bg-primary/50" />
                    </div>
                    <p className="text-white/90 font-medium">
                      AI Coach Avatar Stream — Beyond Presence
                    </p>
                  </div>
                </div>

                {/* Mic control bar */}
                {/* TODO: hook Pause to actually stop audio/transcript capture */}
                <div className="space-y-3">
                  <div className="flex items-center gap-4">
                    <button 
                      className="relative group h-12 w-12 rounded-full bg-gradient-hero flex items-center justify-center shadow-glow-sm hover:shadow-glow transition-all duration-200 hover:scale-105 cursor-pointer flex-shrink-0"
                      aria-label="Speak to coach"
                    >
                      <Mic className="h-5 w-5 text-white" />
                    </button>
                    <button
                      onClick={() => setIsListening(!isListening)}
                      className="px-4 py-2.5 rounded-lg border border-border bg-white hover:bg-gray-50 text-sm font-medium text-foreground transition-colors cursor-pointer flex items-center justify-center gap-2"
                      aria-label={isListening ? "Pause listening" : "Resume listening"}
                    >
                      {isListening ? (
                        <>
                          <Pause className="h-4 w-4" />
                          <span>Pause</span>
                        </>
                      ) : (
                        <>
                          <Play className="h-4 w-4" />
                          <span>Resume</span>
                        </>
                      )}
                    </button>
                  </div>
                  <div className="space-y-1">
                    <p className="text-sm text-muted-foreground">
                      Hold mic and speak. The coach will answer in real time.
                    </p>
                    <p className="text-xs text-muted-foreground/70 italic">
                      You can pause listening at any time.
                    </p>
                  </div>
                </div>
              </div>

              {/* B. Suggested Guidance */}
              <div className="space-y-3 pt-4 border-t border-border">
                <h3 className="text-base font-semibold text-foreground">Suggested Response</h3>
                <p className="text-sm text-foreground leading-relaxed">
                  Supplier is claiming a 15% raw material cost increase. Market data indicates 7–9%. Recommend countering with 8% cap in exchange for 12-month volume commitment.
                </p>
                <div className="flex flex-wrap gap-2 pt-2">
                  <button className="px-4 py-2 rounded-full border border-border bg-white hover:bg-primary/5 hover:border-primary/50 text-sm text-foreground transition-all cursor-pointer">
                    How should I respond right now?
                  </button>
                  <button className="px-4 py-2 rounded-full border border-border bg-white hover:bg-primary/5 hover:border-primary/50 text-sm text-foreground transition-all cursor-pointer">
                    Are they bluffing about cost increases?
                  </button>
                  <button className="px-4 py-2 rounded-full border border-border bg-white hover:bg-primary/5 hover:border-primary/50 text-sm text-foreground transition-all cursor-pointer">
                    Give me a counteroffer.
                  </button>
                </div>
              </div>

              {/* C. Call Transcript */}
              <div className="space-y-3 pt-4 border-t border-border">
                <h3 className="text-base font-semibold text-foreground">Live Transcript</h3>
                {/* TODO: Live ASR transcript injection */}
                <div className="h-40 overflow-y-auto bg-gray-50 rounded-lg p-3 text-sm leading-relaxed space-y-2">
                  <div>
                    <span className="font-medium text-foreground">Supplier:</span>
                    <span className="text-muted-foreground"> We're seeing +15% cost due to nickel and energy.</span>
                  </div>
                  <div>
                    <span className="font-medium text-foreground">You:</span>
                    <span className="text-muted-foreground"> 15% feels high. Help me understand the breakdown?</span>
                  </div>
                  <div className="bg-primary/10 rounded px-2 py-1.5">
                    <span className="font-medium text-primary">Coach Insight:</span>
                    <span className="text-foreground"> Market index for nickel is only up ~7–9%. High bluff likelihood.</span>
                  </div>
                </div>
              </div>
            </div>

            {/* RIGHT COLUMN - Intel & Impact */}
            <div className="bg-white rounded-xl border border-border shadow-sm divide-y divide-border">
              
              {/* Section 1: Current Call Context */}
              <div className="p-6 space-y-4">
                <h3 className="text-base font-semibold text-foreground">Current Call Context</h3>
                {/* TODO: populate from meeting metadata */}
                <div className="space-y-3">
                  <div className="flex justify-between items-start">
                    <span className="text-sm font-medium text-muted-foreground">Supplier:</span>
                    <span className="text-sm text-foreground text-right">ACME Steel GmbH</span>
                  </div>
                  <div className="flex justify-between items-start">
                    <span className="text-sm font-medium text-muted-foreground">Topic:</span>
                    <span className="text-sm text-foreground text-right">Raw material price increase</span>
                  </div>
                  <div className="flex justify-between items-start">
                    <span className="text-sm font-medium text-muted-foreground">Your target:</span>
                    <span className="text-sm text-primary font-medium text-right">-8% vs. their ask</span>
                  </div>
                </div>
              </div>

              {/* Section 2: Financial Impact */}
              <div className="p-6 space-y-4">
                <h3 className="text-base font-semibold text-foreground">Financial Impact</h3>
                <div className="space-y-3">
                  <div className="flex justify-between items-start">
                    <span className="text-sm font-medium text-muted-foreground">Annual spend at current price:</span>
                    <span className="text-sm text-foreground font-semibold">€12.4M</span>
                  </div>
                  <div className="flex justify-between items-start">
                    <span className="text-sm font-medium text-muted-foreground">Cost impact of +12% ask:</span>
                    <span className="text-sm text-destructive font-semibold">+€1.4M / year</span>
                  </div>
                  <div className="flex justify-between items-start">
                    <span className="text-sm font-medium text-muted-foreground">Target counter:</span>
                    <span className="text-sm text-success font-semibold">+6% max = save ~€700k / year</span>
                  </div>
                </div>
                <p className="text-xs text-muted-foreground pt-2">
                  This estimate will be logged and surfaced to Finance.
                </p>
              </div>

              {/* Section 3: Escalation / Next Steps */}
              <div className="p-6 space-y-4">
                <h3 className="text-base font-semibold text-foreground">Next Steps</h3>
                <div className="space-y-2.5">
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
                <div className="pt-4 space-y-2">
                  {/* TODO: escalation brief generator */}
                  <button className="w-full px-4 py-2.5 rounded-lg bg-gradient-hero text-white font-medium hover:shadow-glow-sm transition-all duration-200 hover:scale-[1.02] cursor-pointer">
                    Generate escalation brief
                  </button>
                  <p className="text-xs text-muted-foreground text-center">
                    Creates a summary for leadership with risk, numbers, and ask.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* FULL WIDTH SECTIONS BELOW */}

          {/* Supplier History */}
          <div className="bg-white rounded-xl border border-border shadow-sm p-6 space-y-4">
            <h2 className="text-lg font-semibold text-foreground">Supplier History & Commitments</h2>
            {/* TODO: pull from supplier record / ERP */}
            <div className="space-y-2 text-sm">
              <div className="flex gap-3">
                <span className="text-muted-foreground font-medium">Jul 2025 —</span>
                <span className="text-foreground">Agreed to freeze logistics surcharge until Jan 2026.</span>
              </div>
              <div className="flex gap-3">
                <span className="text-muted-foreground font-medium">May 2025 —</span>
                <span className="text-foreground">Late delivery on Line 3 caused 48h downtime. Escalation to COO.</span>
              </div>
              <div className="flex gap-3">
                <span className="text-muted-foreground font-medium">Feb 2025 —</span>
                <span className="text-foreground">Committed to 45-day payment terms in exchange for guaranteed volume.</span>
              </div>
            </div>
            
            <div className="pt-4 border-t border-border space-y-3">
              <h3 className="text-base font-semibold text-foreground">Open Commitments</h3>
              <div className="space-y-2.5">
                <div className="flex items-start justify-between gap-4">
                  <span className="text-sm text-foreground flex-1">
                    Supplier to provide revised lead time forecast by Oct 28
                  </span>
                  <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-amber-50 text-amber-700 border border-amber-200">
                    Pending
                  </span>
                </div>
                <div className="flex items-start justify-between gap-4">
                  <span className="text-sm text-foreground flex-1">
                    We to review exclusivity clause with Legal
                  </span>
                  <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-blue-50 text-blue-700 border border-blue-200">
                    In review
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Compliance & Risk */}
          <div className="bg-white rounded-xl border border-border shadow-sm p-6 space-y-4">
            <h2 className="text-lg font-semibold text-foreground">Compliance & Risk</h2>
            {/* TODO: policy engine hooks */}
            <div className="space-y-3">
              <div className="flex items-start justify-between gap-4 p-3 rounded-lg bg-amber-50 border border-amber-200">
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
              
              <div className="flex items-start justify-between gap-4 p-3 rounded-lg bg-amber-50 border border-amber-200">
                <div className="flex-1">
                  <div className="font-medium text-sm text-foreground">Exclusivity Language</div>
                  <div className="text-sm text-muted-foreground mt-1">
                    Exclusive supply request mentioned. Legal review required before agreeing.
                  </div>
                </div>
                <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-amber-100 text-amber-800 border border-amber-300 whitespace-nowrap">
                  Action needed
                </span>
              </div>
              
              <div className="flex items-start justify-between gap-4 p-3 rounded-lg bg-blue-50 border border-blue-200">
                <div className="flex-1">
                  <div className="font-medium text-sm text-foreground">Sustainability / ESG</div>
                  <div className="text-sm text-muted-foreground mt-1">
                    No current CO2 reporting on file for this supplier in 2025. Flag for ESG team.
                  </div>
                </div>
                <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 border border-blue-300 whitespace-nowrap">
                  Watch
                </span>
              </div>
            </div>
          </div>

          {/* Executive Impact */}
          <div className="bg-white rounded-xl border border-border shadow-sm p-6 space-y-4">
            <h2 className="text-lg font-semibold text-foreground">Executive Impact</h2>
            {/* TODO: auto-generate CFO/CPO briefing */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="p-4 rounded-lg border border-border bg-gray-50">
                <div className="text-xs text-muted-foreground font-medium uppercase tracking-wider mb-1">
                  Savings vs Supplier Ask
                </div>
                <div className="text-2xl font-semibold text-success">€700k / year</div>
              </div>
              
              <div className="p-4 rounded-lg border border-border bg-gray-50">
                <div className="text-xs text-muted-foreground font-medium uppercase tracking-wider mb-1">
                  Risk Exposure
                </div>
                <div className="text-2xl font-semibold text-destructive">High</div>
                <div className="text-xs text-muted-foreground mt-1">(supply continuity mentioned)</div>
              </div>
              
              <div className="p-4 rounded-lg border border-border bg-gray-50">
                <div className="text-xs text-muted-foreground font-medium uppercase tracking-wider mb-1">
                  Leverage Position
                </div>
                <div className="text-2xl font-semibold text-primary">Strong</div>
                <div className="text-xs text-muted-foreground mt-1">we're 18% of their total volume</div>
              </div>
              
              <div className="p-4 rounded-lg border border-border bg-gray-50">
                <div className="text-xs text-muted-foreground font-medium uppercase tracking-wider mb-1">
                  Next Escalation Owner
                </div>
                <div className="text-lg font-semibold text-foreground">CPO / Head of Procurement</div>
              </div>
            </div>
            
            <p className="text-sm text-muted-foreground leading-relaxed pt-2">
              This negotiation is financially material. If we accept +12%, cost impact is ~€1.4M/year. Coach recommends holding at +6% cap and escalating if they won't move.
            </p>
          </div>

          {/* Footer Legal Note */}
          <div className="text-center pt-4 pb-2">
            <p className="text-xs text-muted-foreground">
              AI-generated strategic guidance. Human approval required before making commercial commitments.
            </p>
          </div>
        </div>
      </div>

      {/* Floating Mini-Player (Picture-in-Picture) */}
      {showFloatingCoach && (
        <div className="fixed bottom-4 right-4 sm:bottom-4 sm:right-4 w-48 sm:w-60 bg-white rounded-xl border border-border shadow-lg z-50 animate-fade-in">
          {/* Header with close button */}
          <div className="flex items-center justify-between p-3 border-b border-border">
            <div className="flex items-center gap-2">
              <Circle className="h-2 w-2 fill-success text-success animate-pulse" />
              <span className="text-xs font-medium text-success">
                {isListening ? "Listening" : "Paused"}
              </span>
            </div>
            <button 
              onClick={() => setShowFloatingCoach(false)}
              className="h-6 w-6 rounded-full hover:bg-gray-100 flex items-center justify-center transition-colors cursor-pointer"
              aria-label="Close floating coach"
            >
              <X className="h-4 w-4 text-muted-foreground" />
            </button>
          </div>

          {/* Mini avatar window */}
          <div className="p-3">
            <div className="relative rounded-lg overflow-hidden bg-gradient-avatar aspect-video flex items-center justify-center border border-border">
              {/* TODO: Embed Beyond Presence avatar iframe/player (mini view) */}
              <div className="text-center space-y-2 px-3">
                <div className="relative w-10 h-10 mx-auto">
                  <div className="absolute inset-0 rounded-full bg-primary/20 animate-pulse" />
                  <div className="absolute inset-2 rounded-full bg-primary/30 animate-pulse" style={{ animationDelay: '150ms' }} />
                  <div className="absolute inset-4 rounded-full bg-primary/50" />
                </div>
                <p className="text-white/90 font-medium text-xs leading-tight">
                  AI Coach Avatar Stream
                </p>
              </div>
            </div>

            {/* Control buttons */}
            <div className="flex items-center gap-2 mt-3">
              <button 
                className="relative group h-10 w-10 rounded-full bg-gradient-hero flex items-center justify-center shadow-glow-sm hover:shadow-glow transition-all duration-200 hover:scale-105 cursor-pointer flex-shrink-0"
                aria-label="Speak to coach"
              >
                <Mic className="h-4 w-4 text-white" />
              </button>
              
              {/* TODO: wire Pause toggle to actually stop listening */}
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

            {/* Helper text */}
            <p className="text-xs text-muted-foreground mt-2 leading-relaxed">
              Hold mic and speak. The coach will answer in real time.
            </p>

            {/* Privacy text */}
            <p className="text-xs text-muted-foreground/70 mt-2 italic">
              You can pause listening at any time.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
