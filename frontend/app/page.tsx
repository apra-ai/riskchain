"use client"

import { useState } from "react"
import { Navigation } from "@/components/navigation"
import { Dashboard } from "@/components/dashboard"
import { ProcessDetail } from "@/components/process-detail"

export default function Home() {
  const [currentView, setCurrentView] = useState<"dashboard" | "process">("dashboard")
  const [selectedProcess, setSelectedProcess] = useState<string | null>(null)

  const handleProcessSelect = (processId: string) => {
    setSelectedProcess(processId)
    setCurrentView("process")
  }

  const handleBackToDashboard = () => {
    setCurrentView("dashboard")
    setSelectedProcess(null)
  }

  return (
    <div className="min-h-screen bg-app-background">
      <Navigation currentView={currentView} onViewChange={setCurrentView} />

      {currentView === "dashboard" ? (
        <Dashboard onProcessSelect={handleProcessSelect} />
      ) : (
        <ProcessDetail onBack={handleBackToDashboard} />
      )}
    </div>
  )
}
