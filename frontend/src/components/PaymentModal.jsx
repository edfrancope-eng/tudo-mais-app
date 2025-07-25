import { useState, useEffect } from 'react'
import { X, Copy, Check, CreditCard, Smartphone } from 'lucide-react'
import { Button } from './ui/button'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Badge } from './ui/badge'
import { useAuth } from '../contexts/AuthContext'

const PaymentModal = ({ isOpen, onClose, planType, planPrice }) => {
  const { token } = useAuth()
  const [paymentInfo, setPaymentInfo] = useState(null)
  const [selectedMethod, setSelectedMethod] = useState('pix')
  const [loading, setLoading] = useState(false)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    if (isOpen && planType) {
      fetchPaymentInfo()
    }
  }, [isOpen, planType])

  const fetchPaymentInfo = async () => {
    setLoading(true)
    try {
      const response = await fetch(`http://localhost:5000/advertiser/payment-info/${planType}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setPaymentInfo(data)
      }
    } catch (error) {
      console.error('Erro ao buscar informações de pagamento:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCopyPix = () => {
    if (paymentInfo?.payment_methods?.pix?.key) {
      navigator.clipboard.writeText(paymentInfo.payment_methods.pix.key)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const handleConfirmPayment = async () => {
    try {
      const response = await fetch('http://localhost:5000/advertiser/confirm-payment', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          plan_type: planType,
          payment_method: selectedMethod
        })
      })

      if (response.ok) {
        const data = await response.json()
        alert(`${data.message}\n\nID do Pagamento: ${data.payment_id}`)
        onClose()
      }
    } catch (error) {
      console.error('Erro ao confirmar pagamento:', error)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-2xl font-bold">
            Pagamento - Plano {planType}
          </h2>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="w-4 h-4" />
          </Button>
        </div>

        <div className="p-6">
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600 mx-auto"></div>
              <p className="mt-2 text-muted-foreground">Carregando informações...</p>
            </div>
          ) : paymentInfo ? (
            <div className="space-y-6">
              {/* Resumo do Plano */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span>Resumo do Pedido</span>
                    <Badge variant="secondary">
                      R$ {planPrice?.toFixed(2)}
                    </Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span>Plano:</span>
                      <span className="font-medium">{planType}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Valor:</span>
                      <span className="font-medium">R$ {planPrice?.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Processamento:</span>
                      <span className="text-sm text-muted-foreground">
                        {paymentInfo.processing_time}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Métodos de Pagamento */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Escolha o método de pagamento:</h3>
                
                <div className="grid gap-4 md:grid-cols-2">
                  {/* PIX */}
                  <Card 
                    className={`cursor-pointer transition-colors ${
                      selectedMethod === 'pix' ? 'border-green-500 bg-green-50' : ''
                    }`}
                    onClick={() => setSelectedMethod('pix')}
                  >
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2 text-base">
                        <Smartphone className="w-5 h-5" />
                        PIX
                        <Badge variant="secondary">Recomendado</Badge>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-muted-foreground">
                        Transferência instantânea e segura
                      </p>
                    </CardContent>
                  </Card>

                  {/* Transferência Bancária */}
                  <Card 
                    className={`cursor-pointer transition-colors ${
                      selectedMethod === 'bank_transfer' ? 'border-green-500 bg-green-50' : ''
                    }`}
                    onClick={() => setSelectedMethod('bank_transfer')}
                  >
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2 text-base">
                        <CreditCard className="w-5 h-5" />
                        Transferência Bancária
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-muted-foreground">
                        Via internet banking ou app do banco
                      </p>
                    </CardContent>
                  </Card>
                </div>
              </div>

              {/* Detalhes do Método Selecionado */}
              {selectedMethod && paymentInfo.payment_methods[selectedMethod] && (
                <Card>
                  <CardHeader>
                    <CardTitle>
                      {paymentInfo.payment_methods[selectedMethod].title}
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <p className="text-muted-foreground">
                      {paymentInfo.payment_methods[selectedMethod].description}
                    </p>

                    {selectedMethod === 'pix' && (
                      <div className="space-y-3">
                        <div className="bg-gray-50 p-4 rounded-lg">
                          <div className="flex items-center justify-between">
                            <div>
                              <p className="font-medium">Chave PIX (CPF):</p>
                              <p className="text-lg font-mono">
                                {paymentInfo.payment_methods.pix.key}
                              </p>
                            </div>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={handleCopyPix}
                              className="flex items-center gap-2"
                            >
                              {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                              {copied ? 'Copiado!' : 'Copiar'}
                            </Button>
                          </div>
                        </div>
                      </div>
                    )}

                    {selectedMethod === 'bank_transfer' && (
                      <div className="bg-gray-50 p-4 rounded-lg space-y-2">
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <span className="font-medium">Banco:</span>
                            <p>{paymentInfo.payment_methods.bank_transfer.bank_details.bank}</p>
                          </div>
                          <div>
                            <span className="font-medium">Agência:</span>
                            <p>{paymentInfo.payment_methods.bank_transfer.bank_details.agency}</p>
                          </div>
                          <div>
                            <span className="font-medium">Conta:</span>
                            <p>{paymentInfo.payment_methods.bank_transfer.bank_details.account}</p>
                          </div>
                          <div>
                            <span className="font-medium">Titular:</span>
                            <p>{paymentInfo.payment_methods.bank_transfer.bank_details.holder}</p>
                          </div>
                        </div>
                      </div>
                    )}

                    <div className="space-y-2">
                      <h4 className="font-medium">Instruções:</h4>
                      <ol className="list-decimal list-inside space-y-1 text-sm text-muted-foreground">
                        {paymentInfo.payment_methods[selectedMethod].instructions.map((instruction, index) => (
                          <li key={index}>{instruction}</li>
                        ))}
                      </ol>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Ações */}
              <div className="flex gap-3">
                <Button
                  onClick={handleConfirmPayment}
                  className="flex-1 bg-green-600 hover:bg-green-700"
                >
                  Confirmar Pagamento
                </Button>
                <Button variant="outline" onClick={onClose}>
                  Cancelar
                </Button>
              </div>

              {/* Suporte */}
              <div className="text-center text-sm text-muted-foreground">
                <p>
                  Dúvidas? Entre em contato: {' '}
                  <a 
                    href={`mailto:${paymentInfo.support_email}`}
                    className="text-green-600 hover:underline"
                  >
                    {paymentInfo.support_email}
                  </a>
                </p>
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-muted-foreground">
                Erro ao carregar informações de pagamento.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default PaymentModal

