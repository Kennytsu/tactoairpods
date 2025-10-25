import { useState, useEffect, useRef } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import {
  Upload,
  FileText,
  TableIcon,
  X,
  Check,
  AlertCircle,
  Download,
  UploadCloud,
  Trash2,
  RefreshCw,
  Save,
  Play,
  ChevronDown,
  Settings,
  Eye,
  Shield,
  Globe,
  Clock,
  AlertTriangle,
  CheckCircle2,
  Loader2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";

// Types
interface UploadedFile {
  id: string;
  name: string;
  size: number;
  type: "pdf" | "csv";
  status: "uploading" | "processing" | "ready" | "error";
  progress: number;
  error?: string;
  extractedText?: string;
  pageCount?: number;
  language?: string;
  isDuplicate?: boolean;
}

interface CSVMapping {
  delimiter: "," | ";" | "\t";
  hasHeader: boolean;
  columns: {
    [key: string]: string; // column name -> mapped field
  };
  preset?: string;
}

interface ContextItem {
  id: string;
  name: string;
  include: boolean;
  role: "Evidence" | "Policy" | "Notes";
  weight: number;
}

interface SetupState {
  sessionId: string;
  scenarioName: string;
  supplierName: string;
  targetGoal: string;
  personaRole: string;
  guardrails: string;
  uploads: UploadedFile[];
  csvMappings: { [fileId: string]: CSVMapping };
  contextItems: ContextItem[];
  language: "EN" | "DE";
  timeLimit: number;
  updatedAt: number;
}

interface RecentSession {
  sessionId: string;
  scenarioName: string;
  supplierName: string;
  updatedAt: number;
}

const PRESET_MAPPINGS = {
  "Tacto Standard (EUR)": {
    delimiter: "," as const,
    hasHeader: true,
    columns: {
      "SKU": "sku",
      "Description": "description",
      "Current Price": "price",
      "% Ask": "percent_ask",
      "Volume": "volume",
    },
  },
  "Generic Spend (USD)": {
    delimiter: ";" as const,
    hasHeader: true,
    columns: {
      "Item": "sku",
      "Name": "description",
      "Price": "price",
      "Increase": "percent_ask",
      "Qty": "volume",
    },
  },
};

export default function CoachSetupPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const sessionIdFromUrl = searchParams.get("session");

  // State
  const [state, setState] = useState<SetupState>({
    sessionId: sessionIdFromUrl || `session-${Date.now()}`,
    scenarioName: "",
    supplierName: "",
    targetGoal: "",
    personaRole: "Procurement Manager",
    guardrails: "",
    uploads: [],
    csvMappings: {},
    contextItems: [],
    language: "EN",
    timeLimit: 60,
    updatedAt: Date.now(),
  });

  const [recentSessions, setRecentSessions] = useState<RecentSession[]>([]);
  const [showResumeDialog, setShowResumeDialog] = useState(false);
  const [pendingSession, setPendingSession] = useState<SetupState | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [dragTarget, setDragTarget] = useState<"pdf" | "csv" | null>(null);
  const [showUnsavedDialog, setShowUnsavedDialog] = useState(false);
  const [pendingNavigation, setPendingNavigation] = useState<string | null>(null);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [showCSVMapper, setShowCSVMapper] = useState<string | null>(null);
  const [showPDFPreview, setShowPDFPreview] = useState<string | null>(null);
  const [selectedPreset, setSelectedPreset] = useState<string>("");
  const [customPresetName, setCustomPresetName] = useState("");

  const fileInputPDFRef = useRef<HTMLInputElement>(null);
  const fileInputCSVRef = useRef<HTMLInputElement>(null);
  const initialStateRef = useRef<string>("");

  // Load from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem("coach-setup-current");
    const recent = localStorage.getItem("coach-setup-recent");

    if (recent) {
      try {
        setRecentSessions(JSON.parse(recent));
      } catch (e) {
        console.error("Failed to parse recent sessions", e);
      }
    }

    if (saved && !sessionIdFromUrl) {
      try {
        const parsed = JSON.parse(saved);
        setPendingSession(parsed);
        setShowResumeDialog(true);
      } catch (e) {
        console.error("Failed to parse saved session", e);
      }
    } else if (sessionIdFromUrl) {
      // Load from recent sessions
      const sessionData = localStorage.getItem(`coach-setup-${sessionIdFromUrl}`);
      if (sessionData) {
        try {
          const parsed = JSON.parse(sessionData);
          setState(parsed);
          initialStateRef.current = JSON.stringify(parsed);
        } catch (e) {
          console.error("Failed to load session", e);
        }
      }
    }

    initialStateRef.current = JSON.stringify(state);
  }, []);

  // Track changes
  useEffect(() => {
    const current = JSON.stringify(state);
    setHasUnsavedChanges(current !== initialStateRef.current);
  }, [state]);

  // Drag & Drop handlers
  useEffect(() => {
    const handleDragOver = (e: DragEvent) => {
      e.preventDefault();
      if (!isDragging) setIsDragging(true);
    };

    const handleDragLeave = (e: DragEvent) => {
      if (e.relatedTarget === null) {
        setIsDragging(false);
        setDragTarget(null);
      }
    };

    const handleDrop = (e: DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      setDragTarget(null);

      const files = Array.from(e.dataTransfer?.files || []);
      if (files.length > 0) {
        handleFilesAdded(files, dragTarget || "pdf");
      }
    };

    window.addEventListener("dragover", handleDragOver);
    window.addEventListener("dragleave", handleDragLeave);
    window.addEventListener("drop", handleDrop);

    return () => {
      window.removeEventListener("dragover", handleDragOver);
      window.removeEventListener("dragleave", handleDragLeave);
      window.removeEventListener("drop", handleDrop);
    };
  }, [isDragging, dragTarget]);

  // Browser back/forward guard
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (hasUnsavedChanges) {
        e.preventDefault();
        e.returnValue = "";
      }
    };

    window.addEventListener("beforeunload", handleBeforeUnload);
    return () => window.removeEventListener("beforeunload", handleBeforeUnload);
  }, [hasUnsavedChanges]);

  // Helper functions
  const saveSession = () => {
    const updated = { ...state, updatedAt: Date.now() };
    setState(updated);
    localStorage.setItem("coach-setup-current", JSON.stringify(updated));
    localStorage.setItem(`coach-setup-${updated.sessionId}`, JSON.stringify(updated));

    // Update recent sessions
    const newRecent: RecentSession = {
      sessionId: updated.sessionId,
      scenarioName: updated.scenarioName || "Untitled",
      supplierName: updated.supplierName,
      updatedAt: updated.updatedAt,
    };

    const updatedRecent = [
      newRecent,
      ...recentSessions.filter((s) => s.sessionId !== updated.sessionId),
    ].slice(0, 3);

    setRecentSessions(updatedRecent);
    localStorage.setItem("coach-setup-recent", JSON.stringify(updatedRecent));
    initialStateRef.current = JSON.stringify(updated);
    setHasUnsavedChanges(false);
  };

  const resumeSession = (session: SetupState) => {
    setState(session);
    initialStateRef.current = JSON.stringify(session);
    setShowResumeDialog(false);
  };

  const discardSession = () => {
    localStorage.removeItem("coach-setup-current");
    setShowResumeDialog(false);
  };

  const deleteSession = (sessionId: string) => {
    localStorage.removeItem(`coach-setup-${sessionId}`);
    const updated = recentSessions.filter((s) => s.sessionId !== sessionId);
    setRecentSessions(updated);
    localStorage.setItem("coach-setup-recent", JSON.stringify(updated));
  };

  const handleFilesAdded = (files: File[], targetType: "pdf" | "csv") => {
    const totalCurrentSize = state.uploads.reduce((sum, f) => sum + f.size, 0);
    const maxTotalSize = 60 * 1024 * 1024; // 60MB
    const maxFileSize = 15 * 1024 * 1024; // 15MB

    const newUploads: UploadedFile[] = [];

    for (const file of files) {
      const ext = file.name.split(".").pop()?.toLowerCase();
      const fileType = ext === "pdf" ? "pdf" : ext === "csv" ? "csv" : null;

      if (!fileType || fileType !== targetType) {
        // Invalid file type
        continue;
      }

      if (file.size > maxFileSize) {
        // File too large
        continue;
      }

      if (totalCurrentSize + file.size > maxTotalSize) {
        // Total size exceeded
        break;
      }

      // Check for duplicates
      const isDuplicate = state.uploads.some(
        (u) => u.name === file.name && u.size === file.size
      );

      const uploadedFile: UploadedFile = {
        id: `file-${Date.now()}-${Math.random()}`,
        name: file.name,
        size: file.size,
        type: fileType,
        status: "uploading",
        progress: 0,
        isDuplicate,
      };

      newUploads.push(uploadedFile);

      // Mock upload progress
      setTimeout(() => mockUploadProgress(uploadedFile.id), 100);
    }

    setState((prev) => ({
      ...prev,
      uploads: [...prev.uploads, ...newUploads],
    }));
  };

  const mockUploadProgress = (fileId: string) => {
    let progress = 0;
    const interval = setInterval(() => {
      progress += Math.random() * 30;
      if (progress >= 100) {
        progress = 100;
        clearInterval(interval);
        setState((prev) => ({
          ...prev,
          uploads: prev.uploads.map((u) =>
            u.id === fileId
              ? { ...u, status: "processing", progress: 100 }
              : u
          ),
        }));
        setTimeout(() => {
          setState((prev) => ({
            ...prev,
            uploads: prev.uploads.map((u) =>
              u.id === fileId
                ? {
                    ...u,
                    status: "ready",
                    extractedText: u.type === "pdf" ? "Sample extracted text..." : undefined,
                    pageCount: u.type === "pdf" ? Math.floor(Math.random() * 50) + 1 : undefined,
                    language: u.type === "pdf" ? "EN" : undefined,
                  }
                : u
            ),
            contextItems: prev.contextItems.concat({
              id: fileId,
              name: prev.uploads.find((u) => u.id === fileId)?.name || "",
              include: true,
              role: "Evidence",
              weight: 50,
            }),
          }));
        }, 1000);
      } else {
        setState((prev) => ({
          ...prev,
          uploads: prev.uploads.map((u) =>
            u.id === fileId ? { ...u, progress } : u
          ),
        }));
      }
    }, 300);
  };

  const removeFile = (fileId: string) => {
    setState((prev) => ({
      ...prev,
      uploads: prev.uploads.filter((u) => u.id !== fileId),
      contextItems: prev.contextItems.filter((c) => c.id !== fileId),
    }));
  };

  const retryFile = (fileId: string) => {
    setState((prev) => ({
      ...prev,
      uploads: prev.uploads.map((u) =>
        u.id === fileId ? { ...u, status: "uploading", progress: 0, error: undefined } : u
      ),
    }));
    setTimeout(() => mockUploadProgress(fileId), 100);
  };

  const applyCSVPreset = (preset: string, fileId: string) => {
    const presetData = PRESET_MAPPINGS[preset as keyof typeof PRESET_MAPPINGS];
    if (presetData) {
      setState((prev) => ({
        ...prev,
        csvMappings: {
          ...prev.csvMappings,
          [fileId]: { ...presetData, preset },
        },
      }));
    }
  };

  const saveCustomPreset = () => {
    if (!customPresetName || !showCSVMapper) return;
    const mapping = state.csvMappings[showCSVMapper];
    if (mapping) {
      localStorage.setItem(
        `csv-preset-${customPresetName}`,
        JSON.stringify(mapping)
      );
      setCustomPresetName("");
    }
  };

  const exportPreset = () => {
    const preset = {
      scenarioName: state.scenarioName,
      supplierName: state.supplierName,
      targetGoal: state.targetGoal,
      personaRole: state.personaRole,
      guardrails: state.guardrails,
      csvMappings: state.csvMappings,
      contextItems: state.contextItems.map((c) => ({
        name: c.name,
        include: c.include,
        role: c.role,
        weight: c.weight,
      })),
      language: state.language,
      timeLimit: state.timeLimit,
    };

    const blob = new Blob([JSON.stringify(preset, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `coach-preset-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const importPreset = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const preset = JSON.parse(event.target?.result as string);
        setState((prev) => ({
          ...prev,
          ...preset,
          sessionId: prev.sessionId, // Keep current session ID
          uploads: prev.uploads, // Keep current uploads
          updatedAt: Date.now(),
        }));
      } catch (e) {
        console.error("Failed to import preset", e);
      }
    };
    reader.readAsText(file);
  };

  const handleStartCoaching = () => {
    saveSession();
    navigate(`/ai-coach?session=${state.sessionId}`);
    {/* TODO: pass sessionId & config to coaching runtime */}
  };

  const handleReset = () => {
    if (hasUnsavedChanges) {
      setPendingNavigation("reset");
      setShowUnsavedDialog(true);
    } else {
      performReset();
    }
  };

  const performReset = () => {
    setState({
      sessionId: `session-${Date.now()}`,
      scenarioName: "",
      supplierName: "",
      targetGoal: "",
      personaRole: "Procurement Manager",
      guardrails: "",
      uploads: [],
      csvMappings: {},
      contextItems: [],
      language: "EN",
      timeLimit: 60,
      updatedAt: Date.now(),
    });
    initialStateRef.current = JSON.stringify(state);
    setHasUnsavedChanges(false);
  };

  const totalUploadSize = state.uploads.reduce((sum, f) => sum + f.size, 0);
  const maxTotalSize = 60 * 1024 * 1024;
  const remainingSize = maxTotalSize - totalUploadSize;

  // Context token estimation (very rough)
  const estimatedTokens = state.contextItems
    .filter((c) => c.include)
    .reduce((sum, c) => {
      const file = state.uploads.find((u) => u.id === c.id);
      if (!file) return sum;
      const textLength = file.extractedText?.length || file.size / 2;
      return sum + Math.floor((textLength / 4) * (c.weight / 50));
    }, 0);

  const contextBudget = 16000;
  const contextUsagePercent = Math.min((estimatedTokens / contextBudget) * 100, 100);

  const relativeTime = (timestamp: number) => {
    const seconds = Math.floor((Date.now() - timestamp) / 1000);
    if (seconds < 60) return "just now";
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Resume Dialog */}
      <Dialog open={showResumeDialog} onOpenChange={setShowResumeDialog}>
        <DialogContent data-testid="setup-resume-dialog">
          <DialogHeader>
            <DialogTitle>Resume Your Setup?</DialogTitle>
            <DialogDescription>
              Resume your last setup from {pendingSession ? relativeTime(pendingSession.updatedAt) : ""}?
              <br />
              <span className="text-xs text-muted-foreground">
                Session ID: {pendingSession?.sessionId}
              </span>
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={discardSession}>
              Discard
            </Button>
            <Button onClick={() => pendingSession && resumeSession(pendingSession)}>
              Resume
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Unsaved Changes Dialog */}
      <Dialog open={showUnsavedDialog} onOpenChange={setShowUnsavedDialog}>
        <DialogContent data-testid="setup-unsaved-dialog">
          <DialogHeader>
            <DialogTitle>Unsaved Changes</DialogTitle>
            <DialogDescription>
              You have unsaved changes. What would you like to do?
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="gap-2">
            <Button
              variant="outline"
              onClick={() => {
                setShowUnsavedDialog(false);
                setPendingNavigation(null);
              }}
            >
              Cancel
            </Button>
            <Button
              variant="outline"
              onClick={() => {
                setShowUnsavedDialog(false);
                if (pendingNavigation === "reset") {
                  performReset();
                }
                setPendingNavigation(null);
              }}
            >
              Leave Anyway
            </Button>
            <Button
              onClick={() => {
                saveSession();
                setShowUnsavedDialog(false);
                if (pendingNavigation === "reset") {
                  performReset();
                }
                setPendingNavigation(null);
              }}
            >
              Save & Leave
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* CSV Mapping Dialog */}
      {showCSVMapper && (
        <Dialog open={!!showCSVMapper} onOpenChange={() => setShowCSVMapper(null)}>
          <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto" data-testid="setup-csv-mapping">
            <DialogHeader>
              <DialogTitle>CSV Column Mapping</DialogTitle>
              <DialogDescription>
                Map your CSV columns to the expected fields
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-6">
              {/* Delimiter & Header Detection */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Delimiter</Label>
                  <Select
                    value={state.csvMappings[showCSVMapper]?.delimiter || ","}
                    onValueChange={(value: any) => {
                      setState((prev) => ({
                        ...prev,
                        csvMappings: {
                          ...prev.csvMappings,
                          [showCSVMapper]: {
                            ...prev.csvMappings[showCSVMapper],
                            delimiter: value,
                          },
                        },
                      }));
                    }}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value=",">Comma (,)</SelectItem>
                      <SelectItem value=";">Semicolon (;)</SelectItem>
                      <SelectItem value="\t">Tab (\t)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="flex items-center gap-2 pt-8">
                  <Checkbox
                    checked={state.csvMappings[showCSVMapper]?.hasHeader ?? true}
                    onCheckedChange={(checked) => {
                      setState((prev) => ({
                        ...prev,
                        csvMappings: {
                          ...prev.csvMappings,
                          [showCSVMapper]: {
                            ...prev.csvMappings[showCSVMapper],
                            hasHeader: checked as boolean,
                          },
                        },
                      }));
                    }}
                  />
                  <Label>Has header row</Label>
                </div>
              </div>

              {/* Preset Selector */}
              <div className="space-y-2">
                <Label>Apply Mapping Preset</Label>
                <div className="flex gap-2">
                  <Select
                    value={selectedPreset}
                    onValueChange={(value) => {
                      setSelectedPreset(value);
                      if (value !== "Custom") {
                        applyCSVPreset(value, showCSVMapper);
                      }
                    }}
                  >
                    <SelectTrigger className="flex-1">
                      <SelectValue placeholder="Select preset..." />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Tacto Standard (EUR)">
                        Tacto Standard (EUR)
                      </SelectItem>
                      <SelectItem value="Generic Spend (USD)">
                        Generic Spend (USD)
                      </SelectItem>
                      <SelectItem value="Custom">Custom...</SelectItem>
                    </SelectContent>
                  </Select>

                  {selectedPreset === "Custom" && (
                    <>
                      <Input
                        placeholder="Preset name"
                        value={customPresetName}
                        onChange={(e) => setCustomPresetName(e.target.value)}
                        className="w-48"
                      />
                      <Button
                        onClick={saveCustomPreset}
                        disabled={!customPresetName}
                        size="sm"
                      >
                        <Save className="h-4 w-4" />
                      </Button>
                    </>
                  )}
                </div>
              </div>

              {/* Mock Preview Table */}
              <div className="space-y-2">
                <Label>Preview (first 5 rows)</Label>
                <div className="border rounded-lg overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-muted">
                      <tr>
                        <th className="px-3 py-2 text-left">SKU</th>
                        <th className="px-3 py-2 text-left">Description</th>
                        <th className="px-3 py-2 text-right">Price</th>
                        <th className="px-3 py-2 text-right">% Ask</th>
                        <th className="px-3 py-2 text-right">Volume</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr className="border-t">
                        <td className="px-3 py-2">SKU-001</td>
                        <td className="px-3 py-2">Steel Sheet 2mm</td>
                        <td className="px-3 py-2 text-right">€45.00</td>
                        <td className="px-3 py-2 text-right">
                          <Badge variant="outline" className="text-red-600">12%</Badge>
                        </td>
                        <td className="px-3 py-2 text-right">1,200</td>
                      </tr>
                      <tr className="border-t">
                        <td className="px-3 py-2">SKU-002</td>
                        <td className="px-3 py-2">Aluminum Bars</td>
                        <td className="px-3 py-2 text-right">€32.50</td>
                        <td className="px-3 py-2 text-right">8%</td>
                        <td className="px-3 py-2 text-right">850</td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                {/* Roll-up preview */}
                <div className="bg-muted/50 rounded-lg p-3 text-sm">
                  <p className="text-muted-foreground">
                    Rows detected: <span className="font-medium text-foreground">1,284</span> |
                    Distinct SKUs: <span className="font-medium text-foreground">312</span> |
                    Est. annual spend: <span className="font-medium text-foreground">€12.4M</span>
                  </p>
                  {/* TODO: compute from mapped columns */}
                </div>
              </div>
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={() => setShowCSVMapper(null)}>
                Close
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}

      {/* PDF Preview Dialog */}
      {showPDFPreview && (
        <Dialog open={!!showPDFPreview} onOpenChange={() => setShowPDFPreview(null)}>
          <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto" data-testid="setup-pdf-preview">
            <DialogHeader>
              <DialogTitle>PDF Preview</DialogTitle>
            </DialogHeader>

            <div className="space-y-4">
              {(() => {
                const file = state.uploads.find((u) => u.id === showPDFPreview);
                if (!file) return null;

                return (
                  <>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-muted-foreground">Pages:</span>{" "}
                        <span className="font-medium">{file.pageCount || "—"}</span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Language:</span>{" "}
                        <Badge variant="outline">{file.language || "EN"}</Badge>
                      </div>
                    </div>

                    <div className="border rounded-lg p-4 bg-muted/30 max-h-96 overflow-y-auto">
                      <p className="text-sm leading-relaxed whitespace-pre-wrap">
                        {file.extractedText || "No text extracted yet."}
                      </p>
                    </div>

                    <Button variant="outline" className="w-full">
                      <Eye className="h-4 w-4 mr-2" />
                      Open Full Preview
                    </Button>
                  </>
                );
              })()}
            </div>

            <DialogFooter>
              <Button onClick={() => setShowPDFPreview(null)}>Close</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}

      {/* Main Content */}
      <div className="max-w-screen-2xl mx-auto p-6 space-y-6">
        {/* Header */}
        <div className="border-b pb-6">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-4xl font-semibold tracking-tight text-foreground">
                Negotiation Coach — Setup
              </h1>
              <p className="text-lg text-muted-foreground mt-2 font-light">
                Configure your scenario, upload context, and prepare for live coaching
              </p>
            </div>
            <Badge variant="outline" className="bg-yellow-50 text-yellow-700 border-yellow-200">
              Pilot Mode
            </Badge>
          </div>

          {/* Recent Sessions */}
          {recentSessions.length > 0 && (
            <div className="mt-6 space-y-3">
              <h3 className="text-sm font-medium text-muted-foreground">Recent Sessions</h3>
              <div className="grid gap-2">
                {recentSessions.map((session) => (
                  <div
                    key={session.sessionId}
                    className="flex items-center justify-between p-3 border rounded-lg bg-card hover:bg-muted/50 transition-colors"
                  >
                    <div className="flex-1">
                      <p className="font-medium text-sm">{session.scenarioName || "Untitled"}</p>
                      <p className="text-xs text-muted-foreground">
                        {session.supplierName} • {relativeTime(session.updatedAt)}
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => {
                          const sessionData = localStorage.getItem(`coach-setup-${session.sessionId}`);
                          if (sessionData) {
                            resumeSession(JSON.parse(sessionData));
                          }
                        }}
                      >
                        Resume
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => deleteSession(session.sessionId)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Main Grid */}
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          {/* LEFT COLUMN - Scenario Configuration */}
          <div className="space-y-6">
            {/* Basic Info */}
            <div className="border rounded-xl p-6 bg-card shadow-sm">
              <h2 className="text-xl font-semibold mb-4">Scenario Details</h2>

              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="scenario-name" data-testid="setup-scenario-name">
                    Scenario Name *
                  </Label>
                  <Input
                    id="scenario-name"
                    placeholder="e.g., ACME Steel Q4 Price Negotiation"
                    value={state.scenarioName}
                    onChange={(e) =>
                      setState((prev) => ({ ...prev, scenarioName: e.target.value }))
                    }
                    aria-label="Scenario name"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="supplier-name">Supplier Name *</Label>
                  <Input
                    id="supplier-name"
                    placeholder="e.g., ACME Steel GmbH"
                    value={state.supplierName}
                    onChange={(e) =>
                      setState((prev) => ({ ...prev, supplierName: e.target.value }))
                    }
                    aria-label="Supplier name"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="target-goal">Your Target Goal *</Label>
                  <Textarea
                    id="target-goal"
                    placeholder="e.g., Counter their +15% ask with max +6% cap tied to volume commitment"
                    value={state.targetGoal}
                    onChange={(e) =>
                      setState((prev) => ({ ...prev, targetGoal: e.target.value }))
                    }
                    rows={3}
                    aria-label="Target goal"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="persona-role">Your Role</Label>
                  <Select
                    value={state.personaRole}
                    onValueChange={(value) =>
                      setState((prev) => ({ ...prev, personaRole: value }))
                    }
                  >
                    <SelectTrigger id="persona-role">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Procurement Manager">Procurement Manager</SelectItem>
                      <SelectItem value="CPO">Chief Procurement Officer</SelectItem>
                      <SelectItem value="Category Lead">Category Lead</SelectItem>
                      <SelectItem value="Sourcing Specialist">Sourcing Specialist</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="guardrails">Company Guardrails & Policies</Label>
                  <Textarea
                    id="guardrails"
                    placeholder="e.g., No exclusivity without Legal review. Prepayment >€250k requires CFO approval."
                    value={state.guardrails}
                    onChange={(e) =>
                      setState((prev) => ({ ...prev, guardrails: e.target.value }))
                    }
                    rows={3}
                    aria-label="Company guardrails"
                  />
                </div>
              </div>
            </div>

            {/* File Uploads */}
            <div className="border rounded-xl p-6 bg-card shadow-sm space-y-6">
              <div>
                <h2 className="text-xl font-semibold">Upload Context</h2>
                <p className="text-sm text-muted-foreground mt-1">
                  Files are processed locally for this demo. Don't upload confidential data.
                </p>
              </div>

              {/* PDF Upload */}
              <div
                className={`border-2 border-dashed rounded-lg p-6 transition-colors ${
                  isDragging && dragTarget === "pdf"
                    ? "border-primary bg-primary/5"
                    : "border-muted-foreground/25"
                }`}
                onDragEnter={() => setDragTarget("pdf")}
                data-testid="setup-upload-pdf"
              >
                <input
                  ref={fileInputPDFRef}
                  type="file"
                  accept=".pdf"
                  multiple
                  className="hidden"
                  onChange={(e) => {
                    if (e.target.files) {
                      handleFilesAdded(Array.from(e.target.files), "pdf");
                    }
                  }}
                  aria-label="Upload PDF files"
                />
                <div className="text-center space-y-3">
                  <FileText className="h-10 w-10 mx-auto text-muted-foreground" />
                  <div>
                    <p className="font-medium">Upload PDF Documents</p>
                    <p className="text-sm text-muted-foreground">
                      Contracts, market reports, supplier docs
                    </p>
                  </div>
                  <Button
                    variant="outline"
                    onClick={() => fileInputPDFRef.current?.click()}
                    className="cursor-pointer"
                  >
                    <UploadCloud className="h-4 w-4 mr-2" />
                    Choose Files
                  </Button>
                  <p className="text-xs text-muted-foreground">
                    .pdf • max 15MB per file
                  </p>
                </div>
              </div>

              {/* CSV Upload */}
              <div
                className={`border-2 border-dashed rounded-lg p-6 transition-colors ${
                  isDragging && dragTarget === "csv"
                    ? "border-primary bg-primary/5"
                    : "border-muted-foreground/25"
                }`}
                onDragEnter={() => setDragTarget("csv")}
                data-testid="setup-upload-csv"
              >
                <input
                  ref={fileInputCSVRef}
                  type="file"
                  accept=".csv"
                  multiple
                  className="hidden"
                  onChange={(e) => {
                    if (e.target.files) {
                      handleFilesAdded(Array.from(e.target.files), "csv");
                    }
                  }}
                  aria-label="Upload CSV files"
                />
                <div className="text-center space-y-3">
                  <TableIcon className="h-10 w-10 mx-auto text-muted-foreground" />
                  <div>
                    <p className="font-medium">Upload CSV Data</p>
                    <p className="text-sm text-muted-foreground">
                      SKU pricing, volume data, historical spend
                    </p>
                  </div>
                  <Button
                    variant="outline"
                    onClick={() => fileInputCSVRef.current?.click()}
                    className="cursor-pointer"
                  >
                    <UploadCloud className="h-4 w-4 mr-2" />
                    Choose Files
                  </Button>
                  <p className="text-xs text-muted-foreground">
                    .csv • max 15MB per file
                  </p>
                </div>
              </div>

              {/* Upload Budget */}
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Remaining upload budget:</span>
                  <span className="font-medium">
                    {(remainingSize / (1024 * 1024)).toFixed(1)}MB / 60MB
                  </span>
                </div>
                <Progress value={(totalUploadSize / maxTotalSize) * 100} />
              </div>

              {/* Uploaded Files List */}
              {state.uploads.length > 0 && (
                <div className="space-y-2">
                  <h3 className="text-sm font-medium">Uploaded Files</h3>
                  <div className="space-y-2">
                    {state.uploads.map((file) => (
                      <div
                        key={file.id}
                        className="border rounded-lg p-3 bg-background space-y-2"
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex items-start gap-2 flex-1 min-w-0">
                            {file.type === "pdf" ? (
                              <FileText className="h-4 w-4 mt-0.5 flex-shrink-0 text-muted-foreground" />
                            ) : (
                              <TableIcon className="h-4 w-4 mt-0.5 flex-shrink-0 text-muted-foreground" />
                            )}
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-medium truncate">{file.name}</p>
                              <p className="text-xs text-muted-foreground">
                                {(file.size / 1024).toFixed(1)} KB
                              </p>
                            </div>
                          </div>

                          <div className="flex items-center gap-2">
                            {file.status === "ready" && file.type === "csv" && (
                              <Badge
                                variant="outline"
                                className="cursor-pointer hover:bg-muted"
                                onClick={() => setShowCSVMapper(file.id)}
                              >
                                {state.csvMappings[file.id] ? "Ready" : "Needs mapping"}
                              </Badge>
                            )}

                            {file.status === "ready" && (
                              <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                                <CheckCircle2 className="h-3 w-3 mr-1" />
                                Ready
                              </Badge>
                            )}

                            {file.status === "error" && (
                              <Badge variant="outline" className="bg-red-50 text-red-700 border-red-200">
                                <AlertCircle className="h-3 w-3 mr-1" />
                                Error
                              </Badge>
                            )}

                            {file.isDuplicate && (
                              <Badge variant="outline" className="bg-yellow-50 text-yellow-700 border-yellow-200">
                                Duplicate?
                              </Badge>
                            )}

                            {file.type === "pdf" && file.status === "ready" && (
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => setShowPDFPreview(file.id)}
                                aria-label="Preview PDF"
                              >
                                <Eye className="h-4 w-4" />
                              </Button>
                            )}

                            {file.status === "error" && (
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => retryFile(file.id)}
                                aria-label="Retry upload"
                              >
                                <RefreshCw className="h-4 w-4" />
                              </Button>
                            )}

                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => removeFile(file.id)}
                              aria-label="Remove file"
                            >
                              <X className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>

                        {(file.status === "uploading" || file.status === "processing") && (
                          <div className="space-y-1">
                            <div className="flex justify-between text-xs">
                              <span className="text-muted-foreground">
                                {file.status === "uploading" ? "Uploading..." : "Processing..."}
                              </span>
                              <span className="font-medium">{Math.floor(file.progress)}%</span>
                            </div>
                            <Progress value={file.progress} />
                          </div>
                        )}

                        {file.error && (
                          <p className="text-xs text-red-600">{file.error}</p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* RIGHT COLUMN - Context Builder & Settings */}
          <div className="space-y-6">
            {/* Context Builder */}
            <div className="border rounded-xl p-6 bg-card shadow-sm space-y-6">
              <div>
                <h2 className="text-xl font-semibold">Context Builder</h2>
                <p className="text-sm text-muted-foreground mt-1">
                  Control what information the coach uses during the negotiation
                </p>
              </div>

              {state.contextItems.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground text-sm">
                  Upload files to build your context
                </div>
              ) : (
                <div className="space-y-3">
                  {state.contextItems.map((item) => (
                    <div
                      key={item.id}
                      className="border rounded-lg p-4 bg-background space-y-3"
                    >
                      <div className="flex items-start gap-3">
                        <Checkbox
                          checked={item.include}
                          onCheckedChange={(checked) => {
                            setState((prev) => ({
                              ...prev,
                              contextItems: prev.contextItems.map((c) =>
                                c.id === item.id ? { ...c, include: checked as boolean } : c
                              ),
                            }));
                          }}
                          aria-label={`Include ${item.name} in context`}
                        />
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium truncate">{item.name}</p>
                          <div className="flex gap-2 mt-2">
                            <Select
                              value={item.role}
                              onValueChange={(value: any) => {
                                setState((prev) => ({
                                  ...prev,
                                  contextItems: prev.contextItems.map((c) =>
                                    c.id === item.id ? { ...c, role: value } : c
                                  ),
                                }));
                              }}
                            >
                              <SelectTrigger className="w-32 h-8 text-xs">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="Evidence">Evidence</SelectItem>
                                <SelectItem value="Policy">Policy</SelectItem>
                                <SelectItem value="Notes">Notes</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>
                        </div>
                      </div>

                      <div className="space-y-2">
                        <div className="flex justify-between text-xs">
                          <span className="text-muted-foreground">Weight</span>
                          <span className="font-medium">{item.weight}</span>
                        </div>
                        <Slider
                          value={[item.weight]}
                          onValueChange={([value]) => {
                            setState((prev) => ({
                              ...prev,
                              contextItems: prev.contextItems.map((c) =>
                                c.id === item.id ? { ...c, weight: value } : c
                              ),
                            }));
                          }}
                          max={100}
                          step={10}
                          aria-label="Context weight"
                        />
                        <p className="text-xs text-muted-foreground">
                          Higher weight = more influence in coaching
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Context Budget Meter */}
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Estimated context tokens:</span>
                  <span className={`font-medium ${estimatedTokens > contextBudget ? 'text-red-600' : ''}`}>
                    {estimatedTokens.toLocaleString()} / {contextBudget.toLocaleString()}
                  </span>
                </div>
                <Progress
                  value={contextUsagePercent}
                  className={contextUsagePercent > 80 ? "[&>div]:bg-red-600" : ""}
                />
                {/* TODO: run rough token estimate from extracted text sizes */}
              </div>
            </div>

            {/* Settings */}
            <div className="border rounded-xl p-6 bg-card shadow-sm space-y-4">
              <h2 className="text-xl font-semibold">Settings</h2>

              <div className="space-y-2">
                <Label htmlFor="language">
                  <Globe className="h-4 w-4 inline mr-2" />
                  Language
                </Label>
                <Select
                  value={state.language}
                  onValueChange={(value: "EN" | "DE") =>
                    setState((prev) => ({ ...prev, language: value }))
                  }
                >
                  <SelectTrigger id="language">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="EN">English (EN)</SelectItem>
                    <SelectItem value="DE">Deutsch (DE)</SelectItem>
                  </SelectContent>
                </Select>
                <p className="text-xs text-muted-foreground">
                  {/* TODO: wire selected language to STT + TTS config */}
                  Sets speech-to-text and coach response language
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="time-limit">
                  <Clock className="h-4 w-4 inline mr-2" />
                  Session Time Limit (minutes)
                </Label>
                <Input
                  id="time-limit"
                  type="number"
                  min={15}
                  max={180}
                  value={state.timeLimit}
                  onChange={(e) =>
                    setState((prev) => ({ ...prev, timeLimit: parseInt(e.target.value) || 60 }))
                  }
                  aria-label="Time limit in minutes"
                />
              </div>
            </div>

            {/* Presets */}
            <div className="border rounded-xl p-6 bg-card shadow-sm space-y-4">
              <h2 className="text-xl font-semibold">Presets</h2>

              <div className="flex gap-2">
                <Button
                  variant="outline"
                  onClick={exportPreset}
                  className="flex-1"
                  disabled={!state.scenarioName}
                >
                  <Download className="h-4 w-4 mr-2" />
                  Export Preset
                </Button>

                <Button
                  variant="outline"
                  onClick={() => document.getElementById("preset-import")?.click()}
                  className="flex-1"
                >
                  <Upload className="h-4 w-4 mr-2" />
                  Import Preset
                </Button>
                <input
                  id="preset-import"
                  type="file"
                  accept=".json"
                  className="hidden"
                  onChange={importPreset}
                />
              </div>

              <Button
                variant="outline"
                onClick={saveSession}
                className="w-full"
                disabled={!state.scenarioName}
              >
                <Save className="h-4 w-4 mr-2" />
                Save as Preset
              </Button>
            </div>
          </div>
        </div>

        {/* Bottom Actions */}
        <div className="flex items-center justify-between border-t pt-6">
          <div className="flex gap-3">
            <Button variant="outline" onClick={handleReset}>
              <Trash2 className="h-4 w-4 mr-2" />
              Reset Setup
            </Button>
            <Button variant="outline" onClick={saveSession} disabled={!state.scenarioName}>
              <Save className="h-4 w-4 mr-2" />
              Save Progress
            </Button>
          </div>

          <Button
            size="lg"
            onClick={handleStartCoaching}
            disabled={!state.scenarioName || !state.supplierName || !state.targetGoal}
            className="bg-gradient-hero hover:shadow-glow transition-all duration-200 hover:scale-105 text-background font-medium"
            data-testid="setup-start-btn"
          >
            <Play className="h-5 w-5 mr-2" />
            Start Coaching
          </Button>
        </div>

        {/* Footer */}
        <div className="text-center text-xs text-muted-foreground pt-6 border-t">
          AI-generated strategic guidance. Human approval required before making commercial
          commitments.
        </div>
      </div>
    </div>
  );
}
