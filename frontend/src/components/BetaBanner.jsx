import { useState, useEffect } from 'react'
import { X, Rocket, Gift } from 'lucide-react'
import { Alert, AlertDescription } from './ui/alert'
import { Button } from './ui/button'
import { Badge } from './ui/badge'

const BetaBanner = () => {
  const [betaStatus, setBetaStatus] = useState(null)
  const [showBanner, setShowBanner] = useState(true)
  const [showMigrationNotice, setShowMigrationNotice] = useState(false)

  useEffect(() => {
    fetchBetaStatus()
    
    // Verificar se deve mostrar aviso de migração
    const lastShown = localStorage.getItem('migration_notice_last_shown')
    const now = new Date()
    
    if (!lastShown) {
      setShowMigrationNotice(true)
    } else {
      const daysSince = (now - new Date(lastShown)) / (1000 * 60 * 60 * 24)
      if (daysSince >= 7) {
        setShowMigrationNotice(true)
      }
    }
  }, [])

  const fetchBetaStatus = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/beta-status')
      if (response.ok) {
        const data = await response.json()
        setBetaStatus(data)
      }
    } catch (error) {
      console.error('Erro ao buscar status beta:', error)
    }
  }

  const dismissMigrationNotice = () => {
    setShowMigrationNotice(false)
    localStorage.setItem('migration_notice_last_shown', new Date().toISOString())
  }

  const dismissBanner = () => {
    setShowBanner(false)
    localStorage.setItem('beta_banner_dismissed', 'true')
  }

  if (!betaStatus?.is_beta) {
    return null
  }

  return (
    <div className="space-y-2">
      {/* Banner Principal Beta */}
      {showBanner && (
        <Alert className="border-green-200 bg-gradient-to-r from-green-50 to-emerald-50">
          <div className="flex items-center justify-between w-full">
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2">
                <Rocket className="w-5 h-5 text-green-600" />
                <Badge variant="secondary" className="bg-green-100 text-green-800 border-green-200">
                  VERSÃO BETA
                </Badge>
              </div>
              
              <AlertDescription className="text-green-800 font-medium">
                {betaStatus.message}
              </AlertDescription>
              
              <div className="flex items-center gap-1">
                <Gift className="w-4 h-4 text-green-600" />
                <span className="text-sm text-green-700 font-medium">
                  Todas as funcionalidades GRÁTIS!
                </span>
              </div>
            </div>
            
            <Button
              variant="ghost"
              size="sm"
              onClick={dismissBanner}
              className="text-green-600 hover:text-green-700 hover:bg-green-100"
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
        </Alert>
      )}

      {/* Aviso de Migração */}
      {showMigrationNotice && (
        <Alert className="border-blue-200 bg-blue-50">
          <div className="flex items-center justify-between w-full">
            <AlertDescription className="text-blue-800">
              {betaStatus.migration_notice}
            </AlertDescription>
            
            <Button
              variant="ghost"
              size="sm"
              onClick={dismissMigrationNotice}
              className="text-blue-600 hover:text-blue-700 hover:bg-blue-100"
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
        </Alert>
      )}
    </div>
  )
}

export default BetaBanner

