"use client"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Bell, Search, Settings, Shield } from "lucide-react"

interface NavigationProps {
  currentView: "dashboard" | "process"
  onViewChange: (view: "dashboard" | "process") => void
}

export function Navigation({ currentView, onViewChange }: NavigationProps) {
  return (
    <nav className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-8">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-semibold text-primary">RiskChain</span>
          </div>

          <div className="hidden md:flex items-center space-x-6">
            <Button
              variant={currentView === "dashboard" ? "default" : "ghost"}
              onClick={() => onViewChange("dashboard")}
              className="text-sm"
            >
              Dashboard
            </Button>
            <Button variant="ghost" className="text-sm text-gray-600">
              Analytics
            </Button>
            <Button variant="ghost" className="text-sm text-gray-600">
              Reports
            </Button>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="icon">
            <Search className="w-5 h-5" />
          </Button>
          <Button variant="ghost" size="icon">
            <Bell className="w-5 h-5" />
          </Button>
          <Button variant="ghost" size="icon">
            <Settings className="w-5 h-5" />
          </Button>

          <div className="flex items-center space-x-3 pl-4 border-l border-gray-200">
            <Avatar className="w-8 h-8">
              <AvatarFallback className="bg-secondary text-white text-sm">JD</AvatarFallback>
            </Avatar>
            <span className="text-sm font-medium text-gray-700">John Doe</span>
          </div>
        </div>
      </div>
    </nav>
  )
}
