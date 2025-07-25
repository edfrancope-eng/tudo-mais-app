import { useState, useEffect } from 'react'
import { Check, Star, Zap, Crown, ExternalLink } from 'lucide-react'
import { Button } from './ui/button'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Badge } from './ui/badge'
import { useAuth } from '../contexts/AuthContext'

const PagSeguroPlans = ({ showTitle = true }) => {
  const { token, user } = useAuth()
  const [plans, setPlans] = useState(null)
  const [loading, setLoading] = useState(true)
  const [subscribing, setSubscribing] = useState(null)

  useEffect(() => {
    fetchPlans()
  }, [])

  const fetchPlans = async () => {
    try {
      const response = await fetch('http://localhost:5000/advertiser/plans')
      if (response.ok) {
        const data = await response.json()
        setPlans(data)
      }
    } catch (error) {
      console.error('Erro ao buscar planos:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubscribe = async (planType) => {
    if (!user) {
      alert('Faça login para assinar um plano')
      return
    }

    setSubscribing(planType)
    
    try {
      const response = await fetch(`http://localhost:5000/advertiser/subscribe/${planType}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        
        // Redirecionar para o PagSeguro
        window.open(data.plan.button_url, '_blank')
        
        // Mostrar instruções
        alert(`Você será redirecionado para o PagSeguro para completar o pagamento do ${data.plan.name}.`)
      } else {
        const error = await response.json()
        alert(error.error || 'Erro ao iniciar assinatura')
      }
    } catch (error) {
      console.error('Erro ao iniciar assinatura:', error)
      alert('Erro de conexão. Tente novamente.')
    } finally {
      setSubscribing(null)
    }
  }

  const getPlanIcon = (planType) => {
    switch (planType) {
      case 'monthly':
        return <Zap className="w-6 h-6" />
      case 'semiannual':
        return <Star className="w-6 h-6" />
      case 'annual':
        return <Crown className="w-6 h-6" />
      default:
        return <Zap className="w-6 h-6" />
    }
  }

  const getPlanColor = (planType) => {
    switch (planType) {
      case 'monthly':
        return 'border-blue-200 hover:border-blue-300'
      case 'semiannual':
        return 'border-green-200 hover:border-green-300'
      case 'annual':
        return 'border-purple-200 hover:border-purple-300 ring-2 ring-purple-100'
      default:
        return 'border-gray-200 hover:border-gray-300'
    }
  }

  const getButtonColor = (planType) => {
    switch (planType) {
      case 'monthly':
        return 'bg-blue-600 hover:bg-blue-700'
      case 'semiannual':
        return 'bg-green-600 hover:bg-green-700'
      case 'annual':
        return 'bg-purple-600 hover:bg-purple-700'
      default:
        return 'bg-gray-600 hover:bg-gray-700'
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        {showTitle && (
          <div className="text-center">
            <h2 className="text-3xl font-bold mb-2">Escolha seu Plano</h2>
            <p className="text-muted-foreground">Selecione o plano ideal para sua empresa</p>
          </div>
        )}
        
        <div className="grid gap-6 md:grid-cols-3">
          {[...Array(3)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-6">
                <div className="space-y-4">
                  <div className="h-6 bg-gray-200 rounded w-1/2"></div>
                  <div className="h-8 bg-gray-200 rounded w-1/3"></div>
                  <div className="space-y-2">
                    {[...Array(4)].map((_, j) => (
                      <div key={j} className="h-4 bg-gray-200 rounded"></div>
                    ))}
                  </div>
                  <div className="h-10 bg-gray-200 rounded"></div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  if (!plans) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Erro ao carregar planos. Tente novamente.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {showTitle && (
        <div className="text-center">
          <h2 className="text-3xl font-bold mb-2">Escolha seu Plano</h2>
          <p className="text-muted-foreground mb-4">
            Selecione o plano ideal para sua empresa crescer
          </p>
          <Badge variant="secondary" className="bg-green-100 text-green-800">
            🚀 Pagamento Seguro via PagSeguro
          </Badge>
        </div>
      )}

      <div className="grid gap-6 md:grid-cols-3">
        {Object.entries(plans).map(([planType, plan]) => (
          <Card 
            key={planType}
            className={`relative transition-all duration-200 ${getPlanColor(planType)} ${
              plan.most_popular ? 'transform scale-105' : ''
            }`}
          >
            {plan.most_popular && (
              <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                <Badge className="bg-purple-600 text-white px-4 py-1">
                  ⭐ Mais Popular
                </Badge>
              </div>
            )}

            <CardHeader className="text-center pb-4">
              <div className="flex items-center justify-center mb-2">
                {getPlanIcon(planType)}
              </div>
              
              <CardTitle className="text-xl">{plan.name}</CardTitle>
              
              <div className="space-y-1">
                <div className="text-3xl font-bold">
                  R$ {plan.price.toFixed(2)}
                </div>
                
                {planType !== 'monthly' && plan.monthly_equivalent && (
                  <div className="text-sm text-muted-foreground">
                    <span className="line-through">
                      R$ {plan.monthly_equivalent.toFixed(2)}
                    </span>
                    <Badge variant="secondary" className="ml-2 bg-green-100 text-green-800">
                      -{plan.savings_percentage}%
                    </Badge>
                  </div>
                )}
                
                <div className="text-sm text-muted-foreground">
                  {planType === 'monthly' && 'por mês'}
                  {planType === 'semiannual' && 'a cada 6 meses'}
                  {planType === 'annual' && 'por ano'}
                </div>
              </div>

              {plan.savings && (
                <div className="text-sm font-medium text-green-600">
                  {plan.savings}
                </div>
              )}
            </CardHeader>

            <CardContent className="space-y-4">
              <div className="space-y-2">
                {plan.features.map((feature, index) => (
                  <div key={index} className="flex items-center gap-2 text-sm">
                    <Check className="w-4 h-4 text-green-600 flex-shrink-0" />
                    <span>{feature}</span>
                  </div>
                ))}
              </div>

              <div className="pt-4">
                <Button
                  onClick={() => handleSubscribe(planType)}
                  disabled={subscribing === planType}
                  className={`w-full ${getButtonColor(planType)}`}
                >
                  {subscribing === planType ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Processando...
                    </>
                  ) : (
                    <>
                      <ExternalLink className="w-4 h-4 mr-2" />
                      Contratar Agora
                    </>
                  )}
                </Button>
              </div>

              {/* Botão HTML do PagSeguro (oculto, usado como fallback) */}
              <div 
                className="hidden"
                dangerouslySetInnerHTML={{ __html: plan.button_html }}
              />
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Informações Adicionais */}
      <div className="text-center space-y-4 pt-6">
        <div className="flex items-center justify-center gap-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-1">
            <Check className="w-4 h-4 text-green-600" />
            <span>Pagamento Seguro</span>
          </div>
          <div className="flex items-center gap-1">
            <Check className="w-4 h-4 text-green-600" />
            <span>Renovação Automática</span>
          </div>
          <div className="flex items-center gap-1">
            <Check className="w-4 h-4 text-green-600" />
            <span>Cancele Quando Quiser</span>
          </div>
        </div>

        <div className="text-xs text-muted-foreground max-w-2xl mx-auto">
          <p>
            * Os pagamentos são processados de forma segura pelo PagSeguro. 
            Você pode cancelar sua assinatura a qualquer momento através da sua conta PagSeguro.
          </p>
          <p className="mt-2">
            * Após a confirmação do pagamento, sua conta será ativada automaticamente.
          </p>
        </div>

        <div className="text-sm">
          <p className="text-muted-foreground">
            Dúvidas? Entre em contato: {' '}
            <a 
              href="mailto:tudomaisapp@hotmail.com"
              className="text-green-600 hover:underline"
            >
              tudomaisapp@hotmail.com
            </a>
          </p>
        </div>
      </div>
    </div>
  )
}

export default PagSeguroPlans

