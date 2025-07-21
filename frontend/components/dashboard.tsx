"use client"

import type React from "react"

import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Truck, Factory, Package, Ship, Plane, ArrowRight, AlertTriangle, TrendingUp, Users } from "lucide-react"

interface Process {
  id: string
  title: string
  description: string
  riskLevel: "High" | "Medium" | "Low"
  steps: number
  icon: React.ComponentType<any>
}

/* const processes: Process[] = [
  {
    id: "1",
    title: "Raw Material Sourcing",
    description: "Procurement of raw materials from global suppliers",
    riskLevel: "High",
    steps: 8,
    icon: Factory,
  },
  {
    id: "2",
    title: "Manufacturing Process",
    description: "Production and quality control in manufacturing facilities",
    riskLevel: "Medium",
    steps: 12,
    icon: Package,
  },
  {
    id: "3",
    title: "Logistics & Transportation",
    description: "Global shipping and distribution network management",
    riskLevel: "High",
    steps: 6,
    icon: Truck,
  },
  {
    id: "4",
    title: "Warehouse Operations",
    description: "Storage and inventory management across facilities",
    riskLevel: "Low",
    steps: 5,
    icon: Package,
  },
  {
    id: "5",
    title: "Maritime Shipping",
    description: "Ocean freight and port operations management",
    riskLevel: "High",
    steps: 9,
    icon: Ship,
  },
  {
    id: "6",
    title: "Air Cargo Operations",
    description: "Express delivery and air freight coordination",
    riskLevel: "Medium",
    steps: 7,
    icon: Plane,
  },
]
 */

const processes: Process[] = [
  {
    id: "1",
    title: "Semiconductor Supply Chain – Asia to Europe",
    description:
      "End-to-end chip supply chain including raw material extraction in China, fabrication in Taiwan by TSMC, and final delivery to Germany",
    riskLevel: "High",
    steps: 6,
    icon: Factory,
  },
  {
    id: "2",
    title: "Battery Cell Manufacturing – South Korea to EU",
    description:
      "Lithium extraction in Chile, refining in South Korea, and battery cell manufacturing and export to European automotive plants",
    riskLevel: "High",
    steps: 7,
    icon: Package,
  },
  {
    id: "3",
    title: "Critical Minerals Supply – Africa to Asia",
    description:
      "Sourcing of cobalt from DRC, shipment to refining plants in China, and redistribution to battery producers in Southeast Asia",
    riskLevel: "High",
    steps: 5,
    icon: Truck,
  },
  {
    id: "4",
    title: "Aftermarket Parts Logistics – EU Domestic",
    description:
      "Warehousing and delivery of aftermarket components for vehicle repairs across central European hubs",
    riskLevel: "Low",
    steps: 4,
    icon: Package,
  },
  {
    id: "5",
    title: "Maritime Container Flow – Asia to EU",
    description:
      "Ocean freight route from Shanghai and Shenzhen to Rotterdam and Hamburg with high seasonal variability",
    riskLevel: "High",
    steps: 6,
    icon: Ship,
  },
  {
    id: "6",
    title: "Air Freight of High-Value Electronics – Global",
    description:
      "Coordinated air cargo for sensitive electronics and critical components from East Asia to Europe and North America",
    riskLevel: "Medium",
    steps: 5,
    icon: Plane,
  },
];


const getRiskColor = (level: string) => {
  switch (level) {
    case "High":
      return "bg-risk-high"
    case "Medium":
      return "bg-risk-medium"
    case "Low":
      return "bg-risk-low"
    default:
      return "bg-gray-500"
  }
}

const getRiskTextColor = (level: string) => {
  switch (level) {
    case "High":
      return "text-risk-high"
    case "Medium":
      return "text-risk-medium"
    case "Low":
      return "text-risk-low"
    default:
      return "text-gray-500"
  }
}

interface DashboardProps {
  onProcessSelect: (processId: string) => void
}

export function Dashboard({ onProcessSelect }: DashboardProps) {
  const highRiskCount = processes.filter((p) => p.riskLevel === "High").length
  const totalProcesses = processes.length

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-primary mb-2">Supply Chain Overview</h1>
        <p className="text-gray-600">Monitor and analyze risks across your supply chain processes</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Processes</p>
                <p className="text-2xl font-bold text-primary">{totalProcesses}</p>
              </div>
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-primary" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">High Risk</p>
                <p className="text-2xl font-bold text-risk-high">{highRiskCount}</p>
              </div>
              <div className="w-12 h-12 bg-risk-high/10 rounded-lg flex items-center justify-center">
                <AlertTriangle className="w-6 h-6 text-risk-high" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Suppliers</p>
                <p className="text-2xl font-bold text-secondary">247</p>
              </div>
              <div className="w-12 h-12 bg-secondary/10 rounded-lg flex items-center justify-center">
                <Users className="w-6 h-6 text-secondary" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Risk Score</p>
                <p className="text-2xl font-bold text-risk-medium">7.2</p>
              </div>
              <div className="w-12 h-12 bg-risk-medium/10 rounded-lg flex items-center justify-center">
                <AlertTriangle className="w-6 h-6 text-risk-medium" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Process Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {processes.map((process) => {
          const IconComponent = process.icon
          return (
            <Card key={process.id} className="hover:shadow-lg transition-shadow cursor-pointer group">
              <CardHeader className="pb-4">
                <div className="flex items-start justify-between">
                  <div
                    className={`w-12 h-12 rounded-lg flex items-center justify-center ${getRiskColor(process.riskLevel)}/10`}
                  >
                    <IconComponent className={`w-6 h-6 ${getRiskTextColor(process.riskLevel)}`} />
                  </div>
                  <Badge variant="secondary" className={`${getRiskColor(process.riskLevel)} text-white`}>
                    {process.riskLevel}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="pt-0">
                <h3 className="font-semibold text-lg text-primary mb-2">{process.title}</h3>
                <p className="text-gray-600 text-sm mb-4 line-clamp-2">{process.description}</p>

                <div className="flex items-center justify-between">
                  <div className="text-sm text-gray-500">{process.steps} steps</div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onProcessSelect(process.id)}
                    className="group-hover:bg-primary group-hover:text-white transition-colors"
                  >
                    View Details
                    <ArrowRight className="w-4 h-4 ml-1" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>
    </div>
  )
}
