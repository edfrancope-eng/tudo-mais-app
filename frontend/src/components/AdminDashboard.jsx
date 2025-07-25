import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Users, DollarSign, Flag, Bell, TrendingUp, Settings } from 'lucide-react'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Label } from './ui/label'
import { Badge } from './ui/badge'
import { useAuth } from '../contexts/AuthContext'
import { Alert, AlertDescription } from './ui/alert'

const AdminDashboard = () => {
  const { user, token, isAdmin } = useAuth()
  const navigate = useNavigate()
  
  const [stats, setStats] = useState({
    totalAdvertisers: 0,
    activeSubscriptions: 0,
    pendingReports: 0,
    newSignups: 0
  })
  
  const [pricing, setPricing] = useState({
    MONTHLY: 10.00,
    SEMI_ANNUAL: 50.00,
    ANNUAL: 100.00
  })
  
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(true)
  const [updateMessage, setUpdateMessage] = useState('')

  useEffect(() => {
    if (!isAdmin()) {
      navigate('/')
      return
    }
    
    fetchDashboardData()
    fetchPricing()
    fetchReports()
  }, [])

  const fetchDashboardData = async () => {
    try {
      const response = await fetch('http://localhost:5000/admin/stats', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setStats(data)
      }
    } catch (error) {
      console.error('Erro ao buscar estatísticas:', error)
    }
  }

  const fetchPricing = async () => {
    try {
      const response = await fetch('http://localhost:5000/admin/pricing', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        const pricingObj = {}
        data.forEach(item => {
          pricingObj[item.plan_type] = item.price
        })
        setPricing(pricingObj)
      }
    } catch (error) {
      console.error('Erro ao buscar preços:', error)
    }
  }

  const fetchReports = async () => {
    try {
      const response = await fetch('http://localhost:5000/admin/reports', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setReports(data)
      }
    } catch (error) {
      console.error('Erro ao buscar denúncias:', error)
    } finally {
      setLoading(false)
    }
  }

  const updatePricing = async (planType, newPrice) => {
    try {
      const response = await fetch('http://localhost:5000/admin/pricing', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          plan_type: planType,
          price: parseFloat(newPrice)
        })
      })

      if (response.ok) {
        setUpdateMessage(`Preço do plano ${planType} atualizado com sucesso!`)
        setTimeout(() => setUpdateMessage(''), 3000)
        fetchPricing()
      }
    } catch (error) {
      console.error('Erro ao atualizar preço:', error)
    }
  }

  const handlePriceChange = (planType, value) => {
    setPricing({
      ...pricing,
      [planType]: value
    })
  }

  const handlePriceSubmit = (planType) => {
    updatePricing(planType, pricing[planType])
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="grid gap-6 md:grid-cols-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">
          Painel Administrativo - <span className="tudo-mais-green">Tudo Mais</span>
        </h1>
        <p className="text-muted-foreground">
          Gerencie sua plataforma de forma completa
        </p>
      </div>

      {updateMessage && (
        <Alert className="mb-6 border-green-200 bg-green-50">
          <AlertDescription className="text-green-800">
            {updateMessage}
          </AlertDescription>
        </Alert>
      )}

      {/* Estatísticas */}
      <div className="grid gap-6 md:grid-cols-4 mb-8">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total de Anunciantes</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalAdvertisers}</div>
            <p className="text-xs text-muted-foreground">
              +{stats.newSignups} novos este mês
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Assinaturas Ativas</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.activeSubscriptions}</div>
            <p className="text-xs text-muted-foreground">
              Pagantes ativos
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Denúncias Pendentes</CardTitle>
            <Flag className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{stats.pendingReports}</div>
            <p className="text-xs text-muted-foreground">
              Requer atenção
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Receita Mensal</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">R$ {(stats.activeSubscriptions * 35).toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              Estimativa baseada na média
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-8 md:grid-cols-2">
        {/* Controle de Preços */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="w-5 h-5" />
              Controle de Preços dos Planos
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-4">
              <div>
                <Label htmlFor="monthly">Plano Mensal (R$)</Label>
                <div className="flex gap-2 mt-1">
                  <Input
                    id="monthly"
                    type="number"
                    step="0.01"
                    value={pricing.MONTHLY}
                    onChange={(e) => handlePriceChange('MONTHLY', e.target.value)}
                    className="flex-1"
                  />
                  <Button 
                    onClick={() => handlePriceSubmit('MONTHLY')}
                    size="sm"
                    className="bg-tudo-mais-green hover:bg-tudo-mais-dark-green"
                  >
                    Atualizar
                  </Button>
                </div>
              </div>

              <div>
                <Label htmlFor="semiannual">Plano Semestral (R$)</Label>
                <div className="flex gap-2 mt-1">
                  <Input
                    id="semiannual"
                    type="number"
                    step="0.01"
                    value={pricing.SEMI_ANNUAL}
                    onChange={(e) => handlePriceChange('SEMI_ANNUAL', e.target.value)}
                    className="flex-1"
                  />
                  <Button 
                    onClick={() => handlePriceSubmit('SEMI_ANNUAL')}
                    size="sm"
                    className="bg-tudo-mais-green hover:bg-tudo-mais-dark-green"
                  >
                    Atualizar
                  </Button>
                </div>
              </div>

              <div>
                <Label htmlFor="annual">Plano Anual (R$)</Label>
                <div className="flex gap-2 mt-1">
                  <Input
                    id="annual"
                    type="number"
                    step="0.01"
                    value={pricing.ANNUAL}
                    onChange={(e) => handlePriceChange('ANNUAL', e.target.value)}
                    className="flex-1"
                  />
                  <Button 
                    onClick={() => handlePriceSubmit('ANNUAL')}
                    size="sm"
                    className="bg-tudo-mais-green hover:bg-tudo-mais-dark-green"
                  >
                    Atualizar
                  </Button>
                </div>
              </div>
            </div>

            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-medium mb-2">Preços Atuais:</h4>
              <div className="space-y-1 text-sm">
                <div>Mensal: <span className="font-semibold">R$ {pricing.MONTHLY}</span></div>
                <div>Semestral: <span className="font-semibold">R$ {pricing.SEMI_ANNUAL}</span></div>
                <div>Anual: <span className="font-semibold">R$ {pricing.ANNUAL}</span></div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Denúncias */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Flag className="w-5 h-5" />
              Denúncias Recentes
              {reports.length > 0 && (
                <Badge variant="destructive">{reports.length}</Badge>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {reports.length === 0 ? (
              <p className="text-muted-foreground text-center py-8">
                Nenhuma denúncia pendente
              </p>
            ) : (
              <div className="space-y-4">
                {reports.slice(0, 5).map((report) => (
                  <div key={report.id} className="border rounded-lg p-4">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h4 className="font-medium">{report.advertiser_name}</h4>
                        <p className="text-sm text-muted-foreground">
                          Denunciado em {new Date(report.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <Badge variant="outline" className="text-red-600 border-red-200">
                        Pendente
                      </Badge>
                    </div>
                    
                    {report.reason && (
                      <p className="text-sm mb-3">{report.reason}</p>
                    )}
                    
                    <div className="flex gap-2">
                      <Button size="sm" variant="outline">
                        Analisar
                      </Button>
                      <Button size="sm" variant="destructive">
                        Suspender
                      </Button>
                    </div>
                  </div>
                ))}
                
                {reports.length > 5 && (
                  <Button variant="outline" className="w-full">
                    Ver todas as denúncias ({reports.length})
                  </Button>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Notificações Sonoras */}
      <div className="mt-8">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bell className="w-5 h-5" />
              Notificações
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium">Avisos Sonoros</h4>
                <p className="text-sm text-muted-foreground">
                  Receba notificações sonoras para novas assinaturas e denúncias
                </p>
              </div>
              <Button variant="outline">
                Configurar
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default AdminDashboard

