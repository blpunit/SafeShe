"use client";

import { useState, useCallback, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  MapPin, Navigation, ShieldCheck, AlertTriangle, Bot, Footprints, Car, Bus, Search, 
  Clock, CloudRain, Users, ArrowLeft, Activity, Info, X, Sparkles
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import SafeMap from "@/components/map/SafeMap";
import { useJourney } from "@/hooks/useJourney";
import { journeyService } from "@/api/services/journeyService";
import { RouteOption } from "@/types/journey";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogClose } from "@/components/ui/dialog";
import { toast } from "sonner";

export default function JourneyPage() {
  const { data, isLoading, planJourney, resetJourney } = useJourney();
  
  // Form State
  const [sourceInput, setSourceInput] = useState("Detecting location...");
  const [destInput, setDestInput] = useState("");
  const [preferences, setPreferences] = useState<string[]>(["safest", "well_lit"]);
  const [userCoords, setUserCoords] = useState<{ lat: number; lng: number } | null>(null);
  
  // Details Modal State
  const [selectedRouteDetail, setSelectedRouteDetail] = useState<RouteOption | null>(null);
  const [activeRouteId, setActiveRouteId] = useState<string | null>(null);
  const [activeGeoJson, setActiveGeoJson] = useState<any | null>(null);

  // Live Monitor State
  const [isJourneyActive, setIsJourneyActive] = useState(false);
  const [agentAlert, setAgentAlert] = useState<any | null>(null);
  const [wsConnection, setWsConnection] = useState<WebSocket | null>(null);

  const togglePreference = (pref: string) => {
    setPreferences(prev => prev.includes(pref) ? prev.filter(p => p !== pref) : [...prev, pref]);
  };

  const handleLocationDetected = useCallback((lat: number, lng: number) => {
    setUserCoords({ lat, lng });
    if (sourceInput === "Detecting location...") {
      setSourceInput(`${lat.toFixed(4)}, ${lng.toFixed(4)}`);
    }
  }, [sourceInput]);

  useEffect(() => {
    if (data?.route_options) {
      const allRoutesGeoJson = {
        type: "FeatureCollection",
        features: data.route_options.map((r: any) => r.geometry)
      };
      setActiveGeoJson(allRoutesGeoJson);
      if (data.recommended_route) {
        setActiveRouteId(data.recommended_route.id);
      }
    }
  }, [data]);

  const handleCalculate = () => {
    if (!destInput) {
      toast.error("Destination Required", { description: "Please enter a destination to calculate a safe route." });
      return;
    }
    
    planJourney({
      source: sourceInput,
      destination: destInput,
      preferences: preferences
    });
  };

  const handleStartJourney = async () => {
    if (!data) return;
    try {
      await journeyService.startJourney(data.journey_id);
      setIsJourneyActive(true);
      
      const ws = journeyService.connectToJourneyWebSocket(data.journey_id, (alertData) => {
        setAgentAlert(alertData);
      });
      setWsConnection(ws);
    } catch (err) {
      console.error("Failed to start journey:", err);
    }
  };

  const handleEndJourney = async () => {
    if (!data) return;
    try {
      await journeyService.cancelJourney(data.journey_id);
      setIsJourneyActive(false);
      if (wsConnection) wsConnection.close();
      setAgentAlert(null);
      resetJourney();
    } catch (err) {
      console.error("Failed to cancel journey:", err);
    }
  };

  const handleCompleteJourney = async () => {
    if (!data) return;
    try {
      await journeyService.completeJourney(data.journey_id);
      setIsJourneyActive(false);
      if (wsConnection) wsConnection.close();
      setAgentAlert(null);
      resetJourney();
      toast.success("Journey Completed", { description: "You have arrived safely." });
    } catch (err) {
      console.error("Failed to complete journey:", err);
      toast.error("Error", { description: "Failed to complete journey." });
    }
  };

  return (
    <div className="grid h-screen w-full grid-cols-1 overflow-hidden bg-background lg:grid-cols-12">
      <aside className="relative z-10 flex h-full flex-col border-r border-border bg-card/60 shadow-[4px_0_24px_rgba(0,0,0,0.02)] backdrop-blur-3xl lg:col-span-4 dark:shadow-[4px_0_24px_rgba(0,0,0,0.2)]">
        
        {/* Top Header */}
        <div className="flex shrink-0 flex-col p-6 lg:p-8 border-b border-border/30">
          <div className="flex items-center justify-between">
            <h1 className="font-[family-name:var(--font-jakarta)] text-3xl font-extrabold tracking-tight text-foreground">
              {data ? "Safe Route" : "Plan Journey"}
            </h1>
            {data && !isJourneyActive && (
              <Button variant="ghost" size="icon" onClick={resetJourney} className="rounded-full hover:bg-secondary">
                <ArrowLeft size={20} />
              </Button>
            )}
          </div>
          
          {!data && (
            <div className="relative mt-8 flex flex-col space-y-4">
              <div className="absolute bottom-8 left-5 top-8 z-0 w-0.5 bg-border" />
              <div className="relative z-10 flex items-center gap-3">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-secondary text-foreground shadow-sm">
                  <Navigation size={18} />
                </div>
                <Input 
                  value={sourceInput}
                  onChange={(e) => setSourceInput(e.target.value)}
                  placeholder="Current Location" 
                  className="h-12 border-border/50 bg-background text-md shadow-sm focus-visible:ring-primary" 
                />
              </div>
              <div className="relative z-10 flex items-center gap-3">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground shadow-sm shadow-primary/20">
                  <MapPin size={18} />
                </div>
                <Input 
                  value={destInput}
                  onChange={(e) => setDestInput(e.target.value)}
                  placeholder="Where to?" 
                  className="h-12 border-border/50 bg-background text-md shadow-sm focus-visible:ring-primary" 
                />
              </div>
            </div>
          )}
        </div>

        <ScrollArea className="flex-1 bg-background/30 p-6 lg:p-8">
          <AnimatePresence mode="wait">
            
            {/* STATE 1: LOADING */}
            {isLoading ? (
              <motion.div key="loading" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="flex flex-col gap-4">
                <div className="flex items-center justify-center p-8 flex-col text-muted-foreground gap-4">
                  <Bot size={48} className="animate-bounce" />
                  <p className="font-semibold text-center">AI Agent coordinating routing, weather, and community reports...</p>
                </div>
                <div className="h-24 animate-pulse rounded-3xl bg-secondary/50" />
                <div className="h-40 animate-pulse rounded-3xl bg-secondary/50" />
              </motion.div>
            ) : 
            
            /* STATE 2: RESULTS */
            data ? (
              <motion.div key="results" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="flex flex-col gap-6">
                
                {/* Safety Score Overview */}
                <div className="glass-card flex items-center justify-between rounded-3xl border-success/30 bg-success/5 p-6">
                  <div className="flex flex-col">
                    <span className="font-[family-name:var(--font-jakarta)] text-xl font-bold text-foreground">Recommended Route</span>
                    <span className="text-sm font-medium text-success flex items-center gap-1 mt-1">
                      <ShieldCheck size={16} /> Risk Level: {data.safety_score > 80 ? 'Low' : data.safety_score > 60 ? 'Moderate' : 'High'}
                    </span>
                  </div>
                  <div className="flex flex-col items-end">
                    <span className="text-4xl font-black text-success">{data.safety_score}<span className="text-xl text-success/70">%</span></span>
                    <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground mt-1">Safety Score</span>
                  </div>
                </div>
                
                {/* AI Recommendation Card */}
                <div className="glass-card flex flex-col gap-3 rounded-3xl border-primary/20 bg-primary/5 p-5 relative overflow-hidden">
                  <div className="absolute top-0 right-0 p-4 opacity-10">
                    <Bot size={80} />
                  </div>
                  <div className="flex items-center gap-2 relative z-10">
                    <Sparkles size={18} className="text-primary" />
                    <span className="font-[family-name:var(--font-jakarta)] text-sm font-bold text-foreground">Agent Analysis ({data.ai_recommendation.confidence}% Confidence)</span>
                  </div>
                  <h3 className="font-bold text-primary relative z-10">{data.ai_recommendation.title}</h3>
                  <p className="text-sm font-medium leading-relaxed text-muted-foreground relative z-10">
                    {data.ai_recommendation.reasoning}
                  </p>
                  
                  {data.ai_recommendation.warnings.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-primary/10 relative z-10">
                      {data.ai_recommendation.warnings.map((w, idx) => (
                        <div key={idx} className="flex items-start gap-2 text-warning text-xs font-semibold">
                          <AlertTriangle size={14} className="shrink-0 mt-0.5" />
                          <span>{w}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Metrics Breakdown */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="glass-card rounded-2xl p-4 flex flex-col">
                    <div className="flex items-center gap-2 text-muted-foreground mb-2">
                      <Clock size={16} /> <span className="text-xs font-bold uppercase">Duration</span>
                    </div>
                    <div className="text-xl font-bold">{Math.ceil(data.recommended_route.estimated_duration / 60)} min</div>
                  </div>
                  <div className="glass-card rounded-2xl p-4 flex flex-col">
                    <div className="flex items-center gap-2 text-muted-foreground mb-2">
                      <Footprints size={16} /> <span className="text-xs font-bold uppercase">Distance</span>
                    </div>
                    <div className="text-xl font-bold">{(data.recommended_route.distance / 1000).toFixed(1)} km</div>
                  </div>
                  <div className="glass-card rounded-2xl p-4 flex flex-col">
                    <div className="flex items-center gap-2 text-info mb-2">
                      <CloudRain size={16} /> <span className="text-xs font-bold uppercase text-muted-foreground">Weather</span>
                    </div>
                    <div className="text-md font-bold">{data.weather_summary.temperature}°C, {data.weather_summary.condition}</div>
                  </div>
                  <div className="glass-card rounded-2xl p-4 flex flex-col">
                    <div className="flex items-center gap-2 text-primary mb-2">
                      <Users size={16} /> <span className="text-xs font-bold uppercase text-muted-foreground">Hazards</span>
                    </div>
                    <div className="text-md font-bold">{data.community_summary.reports_along_route} Active</div>
                  </div>
                </div>

                {/* Alternative Routes */}
                <div className="flex flex-col gap-3">
                  <h3 className="font-[family-name:var(--font-jakarta)] text-sm font-bold uppercase tracking-wider text-muted-foreground ml-1">Available Routes</h3>
                  {data.route_options.map((route) => {
                    return (
                      <div 
                        key={route.id}
                        onClick={() => {
                          setSelectedRouteDetail(route);
                          setActiveRouteId(route.id);
                        }}
                        className={`glass-card flex items-center justify-between rounded-2xl p-4 cursor-pointer transition-all border ${
                          activeRouteId === route.id ? 'border-primary shadow-md shadow-primary/10' : 'border-border/50 hover:border-primary/30'
                        }`}
                      >
                        <div className="flex flex-col">
                          <span className="font-bold text-foreground flex items-center gap-2">
                            {route.name} {route.is_recommended && <span className="text-[10px] bg-primary text-primary-foreground px-2 py-0.5 rounded-full uppercase">AI Pick</span>}
                          </span>
                          <span className="text-xs text-muted-foreground mt-1">
                            {Math.ceil(route.estimated_duration / 60)} min • {(route.distance / 1000).toFixed(1)} km
                          </span>
                        </div>
                        <div className="flex flex-col items-end">
                          <span className={`font-bold ${route.safety_score >= 80 ? 'text-success' : 'text-warning'}`}>{route.safety_score}%</span>
                        </div>
                      </div>
                    );
                  })}
                </div>

                {/* Live Monitoring Area */}
                <div className="mt-4 border-t border-border/50 pt-6 pb-20">
                  {agentAlert && (
                    <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className={`mb-4 glass-card flex flex-col gap-2 rounded-3xl border-${agentAlert.severity === 'high' ? 'destructive' : 'warning'}/50 bg-${agentAlert.severity === 'high' ? 'destructive' : 'warning'}/10 p-5`}>
                      <div className="flex items-center gap-2">
                        <AlertTriangle size={20} className={`text-${agentAlert.severity === 'high' ? 'destructive' : 'warning'}`} />
                        <span className="font-[family-name:var(--font-jakarta)] text-sm font-bold text-foreground">Live Agent Alert</span>
                      </div>
                      <p className="text-sm font-medium leading-relaxed text-foreground">{agentAlert.message}</p>
                      {agentAlert.new_safety_score && (
                        <p className="text-xs font-bold text-destructive">Score Dropped: {agentAlert.new_safety_score}%</p>
                      )}
                    </motion.div>
                  )}

                  {isJourneyActive ? (
                    <div className="flex flex-col gap-3">
                      <Button className="h-14 w-full rounded-2xl bg-success font-bold text-white shadow-lg hover:bg-success/90" onClick={handleCompleteJourney}>
                        <ShieldCheck size={18} className="mr-2" /> Arrived Safely
                      </Button>
                      <Button variant="outline" className="h-14 w-full rounded-2xl font-bold border-border/50 hover:bg-secondary/50" onClick={handleEndJourney}>
                        Cancel Journey
                      </Button>
                    </div>
                  ) : (
                    <Button className="h-14 w-full rounded-2xl bg-primary font-bold text-white shadow-lg shadow-primary/20 hover:bg-primary/90" onClick={handleStartJourney}>
                      <Activity size={18} className="mr-2" /> Start Live Journey Monitor
                    </Button>
                  )}
                </div>
              </motion.div>
            ) : 
            
            /* STATE 3: PLANNER (Default) */
            (
              <motion.div key="planner" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex flex-col gap-8 pb-10">
                
                {/* Preferences */}
                <div>
                  <h3 className="font-[family-name:var(--font-jakarta)] text-sm font-bold mb-3 uppercase tracking-wider text-muted-foreground">AI Routing Preferences</h3>
                  <div className="flex flex-wrap gap-2">
                    <PreferenceChip label="Safest Route" value="safest" active={preferences.includes("safest")} onClick={() => togglePreference("safest")} />
                    <PreferenceChip label="Fastest Route" value="fastest" active={preferences.includes("fastest")} onClick={() => togglePreference("fastest")} />
                    <PreferenceChip label="Avoid Dark Areas" value="avoid_dark" active={preferences.includes("avoid_dark")} onClick={() => togglePreference("avoid_dark")} />
                    <PreferenceChip label="Well Lit Roads" value="well_lit" active={preferences.includes("well_lit")} onClick={() => togglePreference("well_lit")} />
                    <PreferenceChip label="Police Presence" value="police" active={preferences.includes("police")} onClick={() => togglePreference("police")} />
                  </div>
                </div>

                <div className="glass-card p-4 flex items-start gap-3 rounded-2xl bg-secondary/30">
                  <Info size={20} className="text-muted-foreground shrink-0 mt-0.5" />
                  <p className="text-xs text-muted-foreground font-medium">
                    The Agent will orchestrate weather, community reports, and map intelligence to find a path adhering to your preferences.
                  </p>
                </div>

                <Button onClick={handleCalculate} className="btn-premium mt-4 h-14 w-full rounded-2xl bg-foreground text-md font-bold text-background shadow-lg hover:bg-foreground/90">
                  <Search size={18} className="mr-2" /> Ask Agent to Plan Route
                </Button>
              </motion.div>
            )}
          </AnimatePresence>
        </ScrollArea>
      </aside>

      {/* Main Map Area */}
      <main className="relative hidden h-full w-full bg-background lg:col-span-8 lg:block">
        <SafeMap 
          source={null} // Safemap automatically handles GPS fallback
          destination={null}
          routeGeometry={activeGeoJson}
          onLocationDetected={handleLocationDetected}
        />
      </main>

      {/* Route Details Modal */}
      <Dialog open={!!selectedRouteDetail} onOpenChange={(open) => !open && setSelectedRouteDetail(null)}>
        <DialogContent className="sm:max-w-md p-6 bg-card rounded-3xl border-border">
          <DialogHeader>
            <DialogTitle className="text-xl font-bold font-[family-name:var(--font-jakarta)] flex items-center gap-2">
              {selectedRouteDetail?.name}
              {selectedRouteDetail?.is_recommended && <span className="text-[10px] bg-primary text-primary-foreground px-2 py-0.5 rounded-full uppercase ml-2">AI Pick</span>}
            </DialogTitle>
            <DialogDescription>
              Detailed telemetry analysis for this route option.
            </DialogDescription>
          </DialogHeader>
          
          {selectedRouteDetail && (
            <div className="flex flex-col gap-4 mt-2">
              <div className="grid grid-cols-2 gap-4">
                <div className="glass-card rounded-2xl p-4 bg-secondary/30"><div className="text-xs text-muted-foreground uppercase font-bold mb-1">Safety Score</div><div className={`text-2xl font-black ${selectedRouteDetail.safety_score >= 80 ? 'text-success' : 'text-warning'}`}>{selectedRouteDetail.safety_score}%</div></div>
                <div className="glass-card rounded-2xl p-4 bg-secondary/30"><div className="text-xs text-muted-foreground uppercase font-bold mb-1">Duration</div><div className="text-2xl font-black text-foreground">{Math.ceil(selectedRouteDetail.estimated_duration / 60)}m</div></div>
              </div>

              {selectedRouteDetail.warnings.length > 0 && (
                <div className="p-4 rounded-2xl bg-warning/10 border border-warning/20 flex flex-col gap-2">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-warning flex items-center gap-1"><AlertTriangle size={14}/> Risk Factors</h4>
                  {selectedRouteDetail.warnings.map((w, i) => (
                    <p key={i} className="text-sm font-medium text-foreground">{w}</p>
                  ))}
                </div>
              )}

              <Button onClick={() => setSelectedRouteDetail(null)} className="mt-4 w-full rounded-xl">Close Details</Button>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}

// ---------------------------------------------------------
// Sub-components
// ---------------------------------------------------------



function PreferenceChip({ label, value, active, onClick }: { label: string, value: string, active: boolean, onClick: () => void }) {
  return (
    <button onClick={onClick} className={`px-4 py-2 rounded-full text-xs font-semibold border transition-all ${active ? "bg-primary text-primary-foreground border-primary" : "bg-transparent border-border/50 text-muted-foreground hover:border-foreground/30 hover:text-foreground"}`}>
      {label}
    </button>
  );
}