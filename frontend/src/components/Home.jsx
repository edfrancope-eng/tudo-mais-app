import { useState, useEffect } from 'react'
import { Search, MapPin, Star, Phone, Globe, ChevronRight } from 'lucide-react'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Badge } from './ui/badge'
import { useNavigate } from 'react-router-dom'

const Home = () => {
  const [searchQuery, setSearchQuery] = useState('')
  const [top10Advertisers, setTop10Advertisers] = useState([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    fetchTop10Advertisers()
  }, [])

  const fetchTop10Advertisers = async () => {
    try {
      const response = await fetch('http://localhost:5000/advertiser/top10')
      if (response.ok) {
        const data = await response.json()
        setTop10Advertisers(data)
      }
    } catch (error) {
      console.error('Erro ao buscar Top 10:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (e) => {
    e.preventDefault()
    // TODO: Implementar busca
    console.log('Buscar por:', searchQuery)
  }

  const handleAdvertiserClick = (advertiserId) => {
    navigate(`/advertiser/${advertiserId}`)
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

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold mb-4">
          Encontre <span className="tudo-mais-green">tudo</span> e{' '}
          <span className="tudo-mais-red">mais</span> um pouco
        </h1>
        <p className="text-xl text-muted-foreground mb-8">
          O guia completo de serviços e empresas da sua região
        </p>

        {/* Search Bar */}
        <form onSubmit={handleSearch} className="max-w-2xl mx-auto">
          <div className="flex gap-2">
            <Input
              type="text"
              placeholder="Busque por serviços, empresas ou produtos..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="flex-1"
            />
            <Button type="submit" className="bg-tudo-mais-green hover:bg-tudo-mais-dark-green">
              <Search className="w-4 h-4" />
            </Button>
          </div>
        </form>
      </div>

      {/* Top 10 Section */}
      <div className="mb-12">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-3xl font-bold">
            <span className="tudo-mais-red">Top 10</span> Empresas Recentes
          </h2>
          <Badge variant="secondary" className="text-sm">
            Novos cadastros
          </Badge>
        </div>

        {loading ? (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {[...Array(6)].map((_, i) => (
              <Card key={i} className="animate-pulse">
                <CardHeader>
                  <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                </CardHeader>
                <CardContent>
                  <div className="h-20 bg-gray-200 rounded mb-4"></div>
                  <div className="h-3 bg-gray-200 rounded w-full mb-2"></div>
                  <div className="h-3 bg-gray-200 rounded w-2/3"></div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <div className="space-y-6">
            {top10Advertisers.map((advertiser, index) => (
              <Card 
                key={advertiser.id} 
                className="hover:shadow-lg transition-shadow cursor-pointer border-l-4 border-l-green-500"
                onClick={() => handleAdvertiserClick(advertiser.id)}
              >
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-3">
                        <Badge variant="outline" className="tudo-mais-red border-red-500">
                          #{index + 1}
                        </Badge>
                        <h3 className="text-xl font-semibold">{advertiser.business_name}</h3>
                        <Badge variant="secondary">{advertiser.category}</Badge>
                      </div>

                      <div className="flex items-center gap-2 mb-3 text-sm text-muted-foreground">
                        <MapPin className="w-4 h-4" />
                        <span>{advertiser.city}, {advertiser.state}</span>
                      </div>

                      {advertiser.average_rating > 0 && (
                        <div className="flex items-center gap-2 mb-3">
                          <div className="flex">
                            {renderStars(advertiser.average_rating)}
                          </div>
                          <span className="text-sm text-muted-foreground">
                            ({advertiser.average_rating.toFixed(1)})
                          </span>
                        </div>
                      )}

                      <p className="text-muted-foreground mb-4 line-clamp-2">
                        {advertiser.description}
                      </p>

                      {/* Featured Items */}
                      {advertiser.featured_items.length > 0 && (
                        <div className="mb-4">
                          <h4 className="font-medium mb-2">Produtos/Serviços em Destaque:</h4>
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                            {advertiser.featured_items.map((item) => (
                              <div key={item.id} className="bg-gray-50 p-2 rounded text-sm">
                                <div className="font-medium">{item.title}</div>
                                {item.price && (
                                  <div className="text-green-600 font-semibold">{item.price}</div>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      <div className="flex items-center gap-4 text-sm">
                        {advertiser.phone && (
                          <div className="flex items-center gap-1">
                            <Phone className="w-4 h-4" />
                            <span>{advertiser.phone}</span>
                          </div>
                        )}
                        {advertiser.website && (
                          <div className="flex items-center gap-1">
                            <Globe className="w-4 h-4" />
                            <span className="text-blue-600">Site</span>
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center">
                      <ChevronRight className="w-5 h-5 text-muted-foreground" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {!loading && top10Advertisers.length === 0 && (
          <Card>
            <CardContent className="text-center py-12">
              <p className="text-muted-foreground">
                Nenhuma empresa cadastrada ainda. Seja o primeiro a se cadastrar!
              </p>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Call to Action */}
      <div className="text-center bg-gradient-to-r from-green-50 to-red-50 p-8 rounded-lg">
        <h3 className="text-2xl font-bold mb-4">
          Sua empresa ainda não está aqui?
        </h3>
        <p className="text-muted-foreground mb-6">
          Cadastre-se agora e apareça para milhares de clientes em potencial
        </p>
        <Button 
          size="lg" 
          className="bg-tudo-mais-green hover:bg-tudo-mais-dark-green"
          onClick={() => navigate('/register')}
        >
          Cadastrar Minha Empresa
        </Button>
      </div>
    </div>
  )
}

export default Home

