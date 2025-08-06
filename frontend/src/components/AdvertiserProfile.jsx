import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { MapPin, Phone, Globe, Star, Flag } from 'lucide-react'
import { Button } from './ui/button'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Badge } from './ui/badge'

const AdvertiserProfile = () => {
  const { id } = useParams()
  const [advertiser, setAdvertiser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAdvertiser()
  }, [id])

  const fetchAdvertiser = async () => {
    try {
      const response = await fetch(`https://tudo-mais-app-production.up.railway.app/advertiser/${id}`)
      if (response.ok) {
        const data = await response.json()
        setAdvertiser(data)
      }
    } catch (error) {
      console.error('Erro ao buscar anunciante:', error)
    } finally {
      setLoading(false)
    }
  }

  const renderStars = (rating) => {
    const stars = []
    const fullStars = Math.floor(rating)
    const hasHalfStar = rating % 1 !== 0

    for (let i = 0; i < fullStars; i++) {
      stars.push(<Star key={i} className="w-4 h-4 fill-yellow-400 text-yellow-400" />)
    }

    if (hasHalfStar) {
      stars.push(<Star key="half" className="w-4 h-4 fill-yellow-400/50 text-yellow-400" />)
    }

    const emptyStars = 5 - Math.ceil(rating)
    for (let i = 0; i < emptyStars; i++) {
      stars.push(<Star key={`empty-${i}`} className="w-4 h-4 text-gray-300" />)
    }

    return stars
  }

  const handleReport = () => {
    // TODO: Implementar sistema de denúncia
    alert('O perfil será analisado. Agradecemos sua colaboração.')
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid gap-6 md:grid-cols-2">
            <div className="h-64 bg-gray-200 rounded"></div>
            <div className="h-64 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    )
  }

  if (!advertiser) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Card>
          <CardContent className="text-center py-12">
            <p className="text-muted-foreground">Anunciante não encontrado.</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">{advertiser.business_name}</h1>
            <div className="flex items-center gap-2 mb-3 text-muted-foreground">
              <MapPin className="w-4 h-4" />
              <span>{advertiser.city}</span>
              <Badge variant="secondary">{advertiser.category}</Badge>
            </div>
            
            {advertiser.average_rating > 0 && (
              <div className="flex items-center gap-2">
                <div className="flex">
                  {renderStars(advertiser.average_rating)}
                </div>
                <span className="text-sm text-muted-foreground">
                  ({advertiser.average_rating.toFixed(1)})
                </span>
              </div>
            )}
          </div>

          <Button
            variant="outline"
            size="sm"
            onClick={handleReport}
            className="text-red-600 border-red-200 hover:bg-red-50"
          >
            <Flag className="w-4 h-4 mr-2" />
            Denunciar
          </Button>
        </div>
      </div>

      <div className="grid gap-8 md:grid-cols-3">
        {/* Informações da Empresa */}
        <div className="md:col-span-2 space-y-6">
          {/* Descrição */}
          {advertiser.description && (
            <Card>
              <CardHeader>
                <CardTitle>Sobre a Empresa</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground leading-relaxed">
                  {advertiser.description}
                </p>
              </CardContent>
            </Card>
          )}

          {/* Produtos/Serviços */}
          {advertiser.items && advertiser.items.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Produtos e Serviços</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-2">
                  {advertiser.items.map((item) => (
                    <div key={item.id} className="border rounded-lg p-4">
                      {item.image && (
                        <div className="w-full h-32 bg-gray-100 rounded mb-3 flex items-center justify-center">
                          <span className="text-gray-400">Imagem</span>
                        </div>
                      )}
                      <h4 className="font-semibold mb-2">{item.title}</h4>
                      {item.description && (
                        <p className="text-sm text-muted-foreground mb-2">
                          {item.description}
                        </p>
                      )}
                      {item.price && (
                        <p className="font-semibold text-green-600">{item.price}</p>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Sidebar - Contato */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Contato</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {advertiser.phone && (
                <div className="flex items-center gap-3">
                  <Phone className="w-5 h-5 text-green-600" />
                  <div>
                    <p className="font-medium">{advertiser.phone}</p>
                    <Button
                      size="sm"
                      className="mt-1 bg-green-600 hover:bg-green-700"
                      onClick={() => window.open(`tel:${advertiser.phone}`)}
                    >
                      Ligar Agora
                    </Button>
                  </div>
                </div>
              )}

              {advertiser.website && (
                <div className="flex items-center gap-3">
                  <Globe className="w-5 h-5 text-blue-600" />
                  <div>
                    <p className="font-medium">Site</p>
                    <Button
                      size="sm"
                      variant="outline"
                      className="mt-1"
                      onClick={() => window.open(advertiser.website, '_blank')}
                    >
                      Visitar Site
                    </Button>
                  </div>
                </div>
              )}

              {advertiser.address && (
                <div className="flex items-start gap-3">
                  <MapPin className="w-5 h-5 text-red-600 mt-1" />
                  <div>
                    <p className="font-medium">Endereço</p>
                    <p className="text-sm text-muted-foreground">
                      {advertiser.address}
                    </p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Chat */}
          <Card>
            <CardHeader>
              <CardTitle>Conversar</CardTitle>
            </CardHeader>
            <CardContent>
              <Button className="w-full bg-blue-600 hover:bg-blue-700">
                Iniciar Conversa
              </Button>
              <p className="text-xs text-muted-foreground mt-2 text-center">
                Tire suas dúvidas diretamente com a empresa
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default AdvertiserProfile

