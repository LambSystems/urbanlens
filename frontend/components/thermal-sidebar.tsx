'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ChevronLeft, 
  ChevronRight, 
  Flame, 
  BarChart2, 
  Activity
} from 'lucide-react';
import { useThermal } from '@/lib/thermal-context';
import { RankingPanel } from './ranking-panel';
import { TraceTimeline } from './trace-timeline';
import { RecommendationCard } from './recommendation-card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { cn } from '@/lib/utils';

export function ThermalSidebar() {
  const { sidebarOpen, setSidebarOpen, activeHotspot } = useThermal();
  const [activeTab, setActiveTab] = useState('ranking');

  return (
    <>
      {/* Toggle button when closed */}
      <AnimatePresence>
        {!sidebarOpen && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            className="absolute top-4 right-4 z-20"
          >
            <Button
              variant="secondary"
              size="icon"
              onClick={() => setSidebarOpen(true)}
              className="shadow-lg"
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Sidebar panel */}
      <motion.aside
        initial={false}
        animate={{ 
          width: sidebarOpen ? 380 : 0,
          opacity: sidebarOpen ? 1 : 0
        }}
        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
        className={cn(
          "relative h-full border-l border-border bg-sidebar overflow-hidden",
          "flex flex-col"
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-sidebar-border bg-sidebar">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-md bg-primary/10">
              <Flame className="h-4 w-4 text-primary" />
            </div>
            <div>
              <h1 className="text-sm font-semibold text-sidebar-foreground">ThermalGen</h1>
              <p className="text-[10px] text-muted-foreground">Urban Heat Triage</p>
            </div>
          </div>
          
          <Button
            variant="ghost"
            size="icon"
            className="h-7 w-7"
            onClick={() => setSidebarOpen(false)}
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>

        {/* Tabs */}
        <Tabs 
          value={activeTab} 
          onValueChange={setActiveTab}
          className="flex-1 flex flex-col min-h-0"
        >
          <TabsList className="w-full justify-start rounded-none border-b border-sidebar-border bg-transparent px-4 h-10">
            <TabsTrigger 
              value="ranking" 
              className="gap-1.5 data-[state=active]:bg-sidebar-accent"
            >
              <BarChart2 className="h-3.5 w-3.5" />
              <span className="text-xs">Ranking</span>
            </TabsTrigger>
            <TabsTrigger 
              value="trace" 
              className="gap-1.5 data-[state=active]:bg-sidebar-accent"
            >
              <Activity className="h-3.5 w-3.5" />
              <span className="text-xs">Trace</span>
              {activeHotspot && (
                <span className="ml-1 h-1.5 w-1.5 rounded-full bg-primary animate-pulse" />
              )}
            </TabsTrigger>
          </TabsList>

          <TabsContent 
            value="ranking" 
            className="flex-1 m-0 overflow-hidden"
          >
            <RankingPanel />
          </TabsContent>

          <TabsContent 
            value="trace" 
            className="flex-1 m-0 overflow-hidden flex flex-col"
          >
            <div className="flex-1 overflow-hidden">
              <TraceTimeline />
            </div>
            
            {/* Recommendation card at bottom of trace */}
            {activeHotspot && (
              <div className="p-3 border-t border-sidebar-border">
                <RecommendationCard />
              </div>
            )}
          </TabsContent>
        </Tabs>
      </motion.aside>
    </>
  );
}
