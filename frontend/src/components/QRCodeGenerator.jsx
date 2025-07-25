import { useState, useEffect } from 'react'
import { Download, Share2, Copy, Check, QrCode } from 'lucide-react'
import { Button } from './ui/button'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Textarea } from './ui/textarea'
import { useAuth } from '../contexts/AuthContext'

const QRCodeGenerator = () => {
  const { token, isAdmin } = useAuth()
  const [qrData, setQrData] = useState(null)
  const [promotionMaterials, setPromotionMaterials] = useState(null)
  const [loading, setLoading] = useState(true)
  const [copied, setCopied] = useState('')

  useEffect(() => {
    if (isAdmin()) {
      fetchPromotionMaterials()
    }
  }, [])

  const fetchPromotionMaterials = async () => {
    try {
      const response = await fetch('http://localhost:5000/admin/beta-promotion', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setPromotionMaterials(data)
        
        // Buscar QR Code
        const qrResponse = await fetch(data.qr_code_api)
        if (qrResponse.ok) {
          const qrData = await qrResponse.json()
          setQrData(qrData)
        }
      }
    } catch (error) {
      console.error('Erro ao buscar materiais de promoção:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCopy = (text, type) => {
    navigator.clipboard.writeText(text)
    setCopied(type)
    setTimeout(() => setCopied(''), 2000)
  }

  const handleDownloadQR = () => {
    if (qrData?.qr_code) {
      const link = document.createElement('a')
      link.href = qrData.qr_code
      link.download = 'tudo-mais-qr-code.png'
      link.click()
    }
  }

  const handleShare = async (text) => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'Tudo Mais - Versão Beta',
          text: text,
          url: promotionMaterials?.beta_url
        })
      } catch (error) {
        console.log('Erro ao compartilhar:', error)
      }
    } else {
      handleCopy(text, 'share')
    }
  }

  if (!isAdmin()) {
    return null
  }

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="animate-pulse space-y-4">
            <div className="h-6 bg-gray-200 rounded w-1/3"></div>
            <div className="h-32 bg-gray-200 rounded"></div>
            <div className="h-20 bg-gray-200 rounded"></div>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <QrCode className="w-5 h-5" />
            Material de Divulgação - Versão Beta
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* QR Code */}
          {qrData && (
            <div className="text-center space-y-4">
              <div className="inline-block p-4 bg-white border-2 border-gray-200 rounded-lg">
                <img 
                  src={qrData.qr_code} 
                  alt="QR Code Tudo Mais" 
                  className="w-48 h-48 mx-auto"
                />
              </div>
              
              <div className="flex gap-2 justify-center">
                <Button onClick={handleDownloadQR} variant="outline">
                  <Download className="w-4 h-4 mr-2" />
                  Baixar QR Code
                </Button>
                
                <Button 
                  onClick={() => handleCopy(promotionMaterials.beta_url, 'url')}
                  variant="outline"
                >
                  {copied === 'url' ? <Check className="w-4 h-4 mr-2" /> : <Copy className="w-4 h-4 mr-2" />}
                  {copied === 'url' ? 'Copiado!' : 'Copiar Link'}
                </Button>
              </div>
              
              <p className="text-sm text-muted-foreground">
                URL: {promotionMaterials?.beta_url}
              </p>
            </div>
          )}

          {/* Textos para Divulgação */}
          {promotionMaterials && (
            <div className="space-y-4">
              <h3 className="font-semibold">Textos para Divulgação:</h3>
              
              {/* Texto para Redes Sociais */}
              <div className="space-y-2">
                <label className="text-sm font-medium">Para Redes Sociais:</label>
                <div className="relative">
                  <Textarea
                    value={promotionMaterials.promotion_materials.social_media_text}
                    readOnly
                    rows={6}
                    className="pr-20"
                  />
                  <div className="absolute top-2 right-2 flex gap-1">
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleCopy(promotionMaterials.promotion_materials.social_media_text, 'social')}
                    >
                      {copied === 'social' ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleShare(promotionMaterials.promotion_materials.social_media_text)}
                    >
                      <Share2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </div>

              {/* Texto para QR Code */}
              <div className="space-y-2">
                <label className="text-sm font-medium">Para Materiais com QR Code:</label>
                <div className="relative">
                  <Textarea
                    value={promotionMaterials.promotion_materials.qr_code_text}
                    readOnly
                    rows={8}
                    className="pr-20"
                  />
                  <div className="absolute top-2 right-2 flex gap-1">
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleCopy(promotionMaterials.promotion_materials.qr_code_text, 'qr')}
                    >
                      {copied === 'qr' ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                    </Button>
                  </div>
                </div>
              </div>

              {/* Texto para Panfletos */}
              <div className="space-y-2">
                <label className="text-sm font-medium">Para Panfletos/Cartazes:</label>
                <div className="relative">
                  <Textarea
                    value={promotionMaterials.promotion_materials.flyer_text}
                    readOnly
                    rows={6}
                    className="pr-20"
                  />
                  <div className="absolute top-2 right-2">
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleCopy(promotionMaterials.promotion_materials.flyer_text, 'flyer')}
                    >
                      {copied === 'flyer' ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Instruções */}
          {promotionMaterials?.instructions && (
            <div className="space-y-2">
              <h3 className="font-semibold">Instruções de Divulgação:</h3>
              <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
                {promotionMaterials.instructions.map((instruction, index) => (
                  <li key={index}>{instruction}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Links Rápidos */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => window.open(`https://wa.me/?text=${encodeURIComponent(promotionMaterials?.promotion_materials.social_media_text)}`, '_blank')}
            >
              WhatsApp
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => window.open(`https://t.me/share/url?url=${promotionMaterials?.beta_url}&text=${encodeURIComponent(promotionMaterials?.promotion_materials.social_media_text)}`, '_blank')}
            >
              Telegram
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => window.open(`https://www.facebook.com/sharer/sharer.php?u=${promotionMaterials?.beta_url}`, '_blank')}
            >
              Facebook
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(promotionMaterials?.promotion_materials.social_media_text)}`, '_blank')}
            >
              Twitter
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default QRCodeGenerator

