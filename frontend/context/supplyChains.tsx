"use client"
import { createContext, useContext, useEffect, useState } from "react"

type Chain = {
  id: string
  name: string
  riskLevel: "low" | "medium" | "high"
  updatedAt: string
}

interface Process {
  id: string
  title: string
  description: string
  riskLevel: "High" | "Medium" | "Low"
  steps: number
  icon: React.ComponentType<any>
}

const SupplyChainContext = createContext<{
  chains: Chain[]
  loading: boolean
  refetch: () => void
}>({ chains: [], loading: true, refetch: () => {} })

export const SupplyChainProvider = ({ children }: { children: React.ReactNode }) => {
  const [chains, setChains] = useState<Chain[]>([])
  const [loading, setLoading] = useState(true)

  const fetchChains = async () => {
    setLoading(true)
    try {
      const res = await fetch("/api/chains")
      const data = await res.json()
      setChains(data)
    } catch (err) {
      console.error("Fehler beim Laden der Lieferketten:", err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchChains()
  }, [])

  return (
    <SupplyChainContext.Provider value={{ chains, loading, refetch: fetchChains }}>
      {children}
    </SupplyChainContext.Provider>
  )
}

export const useSupplyChains = () => useContext(SupplyChainContext)