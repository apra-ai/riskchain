"use client"

import type React from "react"

import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  ArrowLeft,
  ArrowRight,
  Truck,
  Factory,
  Package,
  Ship,
  MapPin,
  Clock,
  AlertTriangle,
  CheckCircle,
} from "lucide-react"

interface ProcessStep {
  id: string
  title: string
  description: string
  riskScore: number
  riskExplanation: string
  icon: React.ComponentType<any>
  status: "completed" | "active" | "pending"
}

/* const processSteps: ProcessStep[] = [
  {
    id: "1",
    title: "Supplier Selection",
    description: "Evaluate and select raw material suppliers",
    riskScore: 8.5,
    riskExplanation: "Limited supplier diversity in critical regions",
    icon: Factory,
    status: "completed",
  },
  {
    id: "2",
    title: "Order Processing",
    description: "Process purchase orders and contracts",
    riskScore: 3.2,
    riskExplanation: "Automated systems reduce human error risk",
    icon: Package,
    status: "completed",
  },
  {
    id: "3",
    title: "Transport",
    description: "Transportation from supplier to port",
    riskScore: 7.8,
    riskExplanation: "Strike at Rotterdam port affecting schedules",
    icon: Truck,
    status: "active",
  },
  {
    id: "4",
    title: "Port Operations",
    description: "Loading and customs clearance",
    riskScore: 6.5,
    riskExplanation: "Customs delays due to new regulations",
    icon: Ship,
    status: "pending",
  },
  {
    id: "5",
    title: "Maritime Shipping",
    description: "Ocean freight to destination port",
    riskScore: 4.1,
    riskExplanation: "Weather conditions within normal range",
    icon: Ship,
    status: "pending",
  },
  {
    id: "6",
    title: "Final Delivery",
    description: "Last-mile delivery to manufacturing facility",
    riskScore: 5.3,
    riskExplanation: "Traffic congestion in industrial area",
    icon: MapPin,
    status: "pending",
  },
] */

  const processSteps: ProcessStep[] = [
    {
      id: "1",
      title: "Raw Material Sourcing – Baotou, China",
      description: "Rare earth elements and silicon mined and processed in Inner Mongolia",
      riskScore: 8.9,
      riskExplanation: 
        "Export restrictions by Chinese government, high environmental regulation risk, " + 
        "dependency on a single region for rare earths, and high energy consumption in processing.",
      icon: Factory,
      status: "completed",
    },
    {
      id: "2",
      title: "Land Transport to Port – Tianjin, China",
      description: "Transport of processed materials via rail and truck to Tianjin port",
      riskScore: 6.2,
      riskExplanation: 
        "Delays due to overburdened freight rail lines, industrial pollution protests affecting routes, " +
        "and risks of regional COVID-19 shutdowns.",
      icon: Truck,
      status: "completed",
    },
    {
      id: "3",
      title: "Shipping to Taiwan – Port of Taichung",
      description: "Container ship transport from Tianjin to Taichung, Taiwan",
      riskScore: 7.3,
      riskExplanation: 
        "Risk of port congestion, South China Sea geopolitical tensions, " +
        "and potential naval exercises disrupting shipping routes.",
      icon: Ship,
      status: "completed",
    },
    {
      id: "4",
      title: "Semiconductor Fabrication – Hsinchu Science Park, Taiwan",
      description: "Processing of materials and chip manufacturing by TSMC in Hsinchu",
      riskScore: 9.4,
      riskExplanation: 
        "Extreme dependence on a single foundry (TSMC), high earthquake risk, " +
        "water scarcity due to droughts, and threat of Chinese military escalation.",
      icon: Package,
      status: "active",
    },
    {
      id: "5",
      title: "Export to Europe – Port of Hamburg",
      description: "Shipping of finished wafers from Taiwan to Hamburg, Germany",
      riskScore: 6.8,
      riskExplanation: 
        "Maritime bottlenecks (e.g. Suez Canal), long transit time (30+ days), fuel price volatility, " +
        "and container shortages impacting outbound logistics.",
      icon: Ship,
      status: "pending",
    },
    {
      id: "6",
      title: "Final Delivery – Ingolstadt, Germany",
      description: "Truck delivery of chips to a production site in Bavaria (e.g., Audi electronics hub)",
      riskScore: 5.7,
      riskExplanation: 
        "Driver shortage in Europe, diesel cost volatility, and local infrastructure works causing delays.",
      icon: MapPin,
      status: "pending",
    },
  ];  

const getRiskColor = (score: number) => {
  if (score >= 7) return "text-risk-high"
  if (score >= 4) return "text-risk-medium"
  return "text-risk-low"
}

const getRiskBgColor = (score: number) => {
  if (score >= 7) return "bg-risk-high"
  if (score >= 4) return "bg-risk-medium"
  return "bg-risk-low"
}

const getStatusIcon = (status: string) => {
  switch (status) {
    case "completed":
      return <CheckCircle className="w-5 h-5 text-risk-low" />
    case "active":
      return <Clock className="w-5 h-5 text-risk-medium" />
    case "pending":
      return <AlertTriangle className="w-5 h-5 text-gray-400" />
    default:
      return null
  }
}

interface ProcessDetailProps {
  onBack: () => void
}

export function ProcessDetail({ onBack }: ProcessDetailProps) {
  const averageRisk = processSteps.reduce((sum, step) => sum + step.riskScore, 0) / processSteps.length

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <Button variant="ghost" onClick={onBack} className="mb-4 text-primary hover:text-primary">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Dashboard
        </Button>

        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-primary mb-2">Raw Material Sourcing</h1>
            <p className="text-gray-600">Procurement of raw materials from global suppliers</p>
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-500 mb-1">Average Risk Score</div>
            <div className={`text-2xl font-bold ${getRiskColor(averageRisk)}`}>{averageRisk.toFixed(1)}</div>
          </div>
        </div>
      </div>

      {/* Process Chain */}
      <Card className="mb-8">
        <CardContent className="p-8">
          <h2 className="text-xl font-semibold text-primary mb-6">Process Flow</h2>

          <div className="relative">
            {/* Desktop horizontal layout */}
            <div className="hidden lg:flex items-center justify-between overflow-x-auto pb-4">
              <div className="flex items-center justify-between w-full">
                {processSteps.map((step, index) => {
                  const IconComponent = step.icon
                  return (
                    <div key={step.id} className="flex items-center">
                      <div className="flex flex-col items-center">
                        {/* Step Card */}
                        <div className="min-h-[400px] bg-white border-2 border-gray-200 rounded-xl p-6 w-64 shadow-sm hover:shadow-md transition-shadow">
                          <div className="flex items-center justify-between mb-4">
                            <div
                              className={`w-12 h-12 rounded-lg flex items-center justify-center ${getRiskBgColor(step.riskScore)}/10`}
                            >
                              <IconComponent className={`w-6 h-6 ${getRiskColor(step.riskScore)}`} />
                            </div>
                            {getStatusIcon(step.status)}
                          </div>

                          <h3 className="font-semibold text-primary mb-2">{step.title}</h3>
                          <p className="text-sm text-gray-600 mb-4">{step.description}</p>

                          <div className="space-y-2">
                            <div className="flex items-center justify-between">
                              <span className="text-sm text-gray-500">Risk Score</span>
                              <Badge variant="secondary" className={`${getRiskBgColor(step.riskScore)} text-white`}>
                                {step.riskScore}
                              </Badge>
                            </div>
                            <p className="text-xs text-gray-500 italic">{step.riskExplanation}</p>
                          </div>
                        </div>
                      </div>

                      {/* Arrow between steps */}
                      {index < processSteps.length - 1 && <ArrowRight className="w-6 h-6 text-gray-400 mx-4" />}
                    </div>
                  )
                })}
              </div>
            </div>

            {/* Mobile vertical layout */}
            <div className="lg:hidden space-y-4">
              {processSteps.map((step, index) => {
                const IconComponent = step.icon
                return (
                  <div key={step.id}>
                    <div className="bg-white border-2 border-gray-200 rounded-xl p-6 shadow-sm">
                      <div className="flex items-start space-x-4">
                        <div
                          className={`w-12 h-12 rounded-lg flex items-center justify-center ${getRiskBgColor(step.riskScore)}/10 flex-shrink-0`}
                        >
                          <IconComponent className={`w-6 h-6 ${getRiskColor(step.riskScore)}`} />
                        </div>

                        <div className="flex-1">
                          <div className="flex items-center justify-between mb-2">
                            <h3 className="font-semibold text-primary">{step.title}</h3>
                            {getStatusIcon(step.status)}
                          </div>

                          <p className="text-sm text-gray-600 mb-3">{step.description}</p>

                          <div className="flex items-center justify-between mb-2">
                            <span className="text-sm text-gray-500">Risk Score</span>
                            <Badge variant="secondary" className={`${getRiskBgColor(step.riskScore)} text-white`}>
                              {step.riskScore}
                            </Badge>
                          </div>
                          <p className="text-xs text-gray-500 italic">{step.riskExplanation}</p>
                        </div>
                      </div>
                    </div>

                    {/* Vertical arrow */}
                    {index < processSteps.length - 1 && (
                      <div className="flex justify-center py-2">
                        <ArrowRight className="w-6 h-6 text-gray-400 rotate-90" />
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Risk Summary */}
{/*       <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">High Risk Steps</p>
                <p className="text-2xl font-bold text-risk-high">
                  {processSteps.filter((s) => s.riskScore >= 7).length}
                </p>
              </div>
              <AlertTriangle className="w-8 h-8 text-risk-high" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Completed Steps</p>
                <p className="text-2xl font-bold text-risk-low">
                  {processSteps.filter((s) => s.status === "completed").length}
                </p>
              </div>
              <CheckCircle className="w-8 h-8 text-risk-low" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Est. Completion</p>
                <p className="text-2xl font-bold text-secondary">14 days</p>
              </div>
              <Clock className="w-8 h-8 text-secondary" />
            </div>
          </CardContent>
        </Card>
      </div> */}
    </div>
  )
}
