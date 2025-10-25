import { useState, useMemo } from 'react';

export interface FinancialContext {
  currentSpend: number; // Annual spend at current price
  supplierAsk: number; // Percentage increase supplier is asking for
  targetCounter: number; // Our target counter percentage
  costImpact: number; // Cost impact of supplier's ask
  potentialSavings: number; // Potential savings with our counter
  leveragePosition: string; // Our leverage position
  riskExposure: string; // Risk exposure level
  nextEscalationOwner: string; // Who to escalate to
}

export const useFinancialContext = () => {
  // TODO: This should eventually come from scenario configuration
  const [financialData] = useState<FinancialContext>({
    currentSpend: 12400000, // €12.4M
    supplierAsk: 12, // +12%
    targetCounter: 6, // +6%
    leveragePosition: "Strong",
    riskExposure: "High",
    nextEscalationOwner: "CPO / Head of Procurement"
  });

  const calculatedValues = useMemo(() => {
    const costImpact = (financialData.currentSpend * financialData.supplierAsk) / 100;
    const potentialSavings = (financialData.currentSpend * (financialData.supplierAsk - financialData.targetCounter)) / 100;
    
    return {
      ...financialData,
      costImpact,
      potentialSavings
    };
  }, [financialData]);

  const formatCurrency = (amount: number): string => {
    if (amount >= 1000000) {
      return `€${(amount / 1000000).toFixed(1)}M`;
    }
    return `€${amount.toLocaleString()}`;
  };

  const formatPercentage = (percentage: number): string => {
    return `${percentage > 0 ? '+' : ''}${percentage}%`;
  };

  return {
    ...calculatedValues,
    formatCurrency,
    formatPercentage
  };
};
