'use client';

import { motion } from 'framer-motion';
import { 
  Lightbulb, 
  ArrowRight, 
  DollarSign, 
  ThermometerSnowflake,
  ChevronDown,
  ChevronUp,
  AlertCircle
} from 'lucide-react';
import { useState } from 'react';
import { useThermal } from '@/lib/thermal-context';
import { getHotspotTypeLabel } from '@/lib/hotspot-labels';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

const PRIORITY_CONFIG = {
  high: { color: 'bg-red-500/10 text-red-500 border-red-500/20', label: 'High Priority' },
  medium: { color: 'bg-amber-500/10 text-amber-500 border-amber-500/20', label: 'Medium Priority' },
  low: { color: 'bg-green-500/10 text-green-500 border-green-500/20', label: 'Low Priority' },
};

export function RecommendationCard() {
  const { activeHotspot, recommendations } = useThermal();
  const [expandedAction, setExpandedAction] = useState<string | null>(null);

  if (!activeHotspot) {
    return null;
  }

  const recommendation = recommendations[activeHotspot.id];
  
  if (!recommendation || activeHotspot.status === 'discarded') {
    if (activeHotspot.status === 'investigating') {
      return (
        <Card className="border-amber-500/30 bg-amber-500/5">
          <CardContent className="p-4">
            <div className="flex items-start gap-3">
              <div className="p-2 rounded-full bg-amber-500/10">
                <AlertCircle className="h-4 w-4 text-amber-500" />
              </div>
              <div>
                <p className="text-sm font-medium text-amber-500">Investigation in Progress</p>
                <p className="text-xs text-muted-foreground mt-1">
                  Recommendations will be generated once the agent completes its analysis.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      );
    }
    
    if (activeHotspot.status === 'discarded') {
      return (
        <Card className="border-muted bg-muted/30">
          <CardContent className="p-4">
            <div className="flex items-start gap-3">
              <div className="p-2 rounded-full bg-muted">
                <AlertCircle className="h-4 w-4 text-muted-foreground" />
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">No Action Required</p>
                <p className="text-xs text-muted-foreground mt-1">
                  This hotspot was identified as an expected heat source and has been discarded.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      );
    }
    
    return null;
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card className="border-primary/30 bg-primary/5">
        <CardHeader className="pb-3">
          <div className="flex items-start gap-3">
            <div className="p-2 rounded-full bg-primary/10">
              <Lightbulb className="h-4 w-4 text-primary" />
            </div>
            <div className="flex-1 min-w-0">
              <CardTitle className="text-sm font-medium">
                Recommendation for {getHotspotTypeLabel(activeHotspot.type)}
              </CardTitle>
              <p className="text-xs text-muted-foreground mt-1 leading-relaxed">
                {recommendation.summary}
              </p>
            </div>
          </div>
        </CardHeader>
        
        <CardContent className="pt-0 space-y-3">
          {/* Impact metrics */}
          <div className="flex items-center gap-4 p-2 rounded-lg bg-muted/50">
            <div className="flex items-center gap-2">
              <DollarSign className="h-3.5 w-3.5 text-muted-foreground" />
              <div>
                <p className="text-[10px] text-muted-foreground uppercase tracking-wider">Est. Cost</p>
                <p className="text-xs font-medium">{recommendation.estimatedCostRange}</p>
              </div>
            </div>
            <div className="w-px h-8 bg-border" />
            <div className="flex items-center gap-2">
              <ThermometerSnowflake className="h-3.5 w-3.5 text-muted-foreground" />
              <div>
                <p className="text-[10px] text-muted-foreground uppercase tracking-wider">Temp Reduction</p>
                <p className="text-xs font-medium">{recommendation.estimatedTemperatureReduction}</p>
              </div>
            </div>
          </div>
          
          {/* Action items */}
          <div className="space-y-2">
            <p className="text-[10px] uppercase tracking-wider text-muted-foreground font-medium">
              Recommended Actions
            </p>
            
            {recommendation.actions.map((action) => {
              const isExpanded = expandedAction === action.id;
              const priorityConfig = PRIORITY_CONFIG[action.priority];
              
              return (
                <div 
                  key={action.id}
                  className="rounded-lg border border-border bg-card overflow-hidden"
                >
                  <button
                    onClick={() => setExpandedAction(isExpanded ? null : action.id)}
                    className="w-full flex items-center gap-3 p-3 text-left hover:bg-muted/50 transition-colors"
                  >
                    <Badge 
                      variant="outline" 
                      className={cn("text-[10px] shrink-0", priorityConfig.color)}
                    >
                      {priorityConfig.label}
                    </Badge>
                    <span className="flex-1 text-sm font-medium truncate">
                      {action.title}
                    </span>
                    {isExpanded ? (
                      <ChevronUp className="h-4 w-4 text-muted-foreground shrink-0" />
                    ) : (
                      <ChevronDown className="h-4 w-4 text-muted-foreground shrink-0" />
                    )}
                  </button>
                  
                  {isExpanded && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.2 }}
                      className="border-t border-border"
                    >
                      <div className="p-3 space-y-2">
                        <p className="text-xs text-muted-foreground leading-relaxed">
                          {action.description}
                        </p>
                        <div className="flex items-center gap-1.5 text-xs text-primary">
                          <ArrowRight className="h-3 w-3" />
                          <span className="font-medium">{action.estimatedImpact}</span>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </div>
              );
            })}
          </div>
          
          {/* Action button */}
          <Button className="w-full mt-2" size="sm">
            Generate Detailed Report
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </CardContent>
      </Card>
    </motion.div>
  );
}
