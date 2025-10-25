import { Button } from "@/components/ui/button";
import { ArrowRight, Sparkles } from "lucide-react";
import { Link } from "react-router-dom";

const Index = () => {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <div className="text-center space-y-8 px-6">
        <div className="inline-flex items-center justify-center">
          <div className="w-16 h-16 rounded-2xl bg-gradient-hero flex items-center justify-center shadow-glow">
            <Sparkles className="h-8 w-8 text-background" />
          </div>
        </div>
        <div className="space-y-3">
          <h1 className="text-5xl font-semibold tracking-tight text-foreground">
            AI Negotiation Coach
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto font-light leading-relaxed">
            Experience real-time AI guidance during supplier negotiations
          </p>
        </div>
        <Link to="/ai-coach">
          <Button 
            size="lg" 
            className="bg-gradient-hero hover:shadow-glow transition-all duration-200 hover:scale-105 text-background font-medium"
          >
            View Demo
            <ArrowRight className="ml-2 h-5 w-5" />
          </Button>
        </Link>
      </div>
    </div>
  );
};

export default Index;
