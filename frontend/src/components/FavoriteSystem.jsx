import { useState, useEffect } from 'react'
import { Heart, MapPin, Star } from 'lucide-react'
import { Button } from './ui/button'
import { Card, CardContent } from './ui/card'
import { Badge } from './ui/badge'
import { useAuth } from '../contexts/AuthContext'
import { useNavigate } from 'react-router-dom'

const FavoriteButton = ({ advertiserId, className = "" }) => {
  const { user, token } = useAuth()
  const [isFavorite, setIsFavorite] = useState(false)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (user && advertiserId) {
      checkFavoriteStatus()
    }
  }, [user, advertiserId])

  const checkFavoriteStatus = async () => {
    try {
      const response = await fetch(`http://localhost:5000/user/favorites/${advertiserId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setIsFavorite(data.is_favorite)
      }
    } catch (error) {
      console.error('Erro ao verificar favorito:', error)
    }
  }

  const toggleFavorite = async () => {
    if (!user) {
      alert('Faça login para adicionar aos favoritos')
      return
    }

    setLoading(true)
    try {
      const method = isFavorite ? 'DELETE' : 'POST'
      const response = await fetch(`http://localhost:5000/user/favorites/${advertiserId}`, {
        method,
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        setIsFavorite(!isFavorite)
      }
    } catch (error) {
      console.error('Erro ao alterar favorito:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={toggleFavorite}
      disabled={loading}
      className={`${className} ${isFavorite ? 'text-red-600 hover:text-red-700' : 'text-gray-400 hover:text-red-600'}`}
    >
      <Heart className={`w-5 h-5 ${isFavorite ? 'fill-current' : ''}`} />
    </Button>
  )
}

const FavoritesList = () => {
  const { user, token } = useAuth()
  const navigate = useNavigate()
  const [favorites, setFavorites] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (user) {
      fetchFavorites()
    }
  }, [user])

  const fetchFavorites = async () => {
    try {
      const response = await fetch('http://localhost:5000/user/favorites', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setFavorites(data)
      }
    } catch (error) {
      console.error('Erro ao buscar favoritos:', error)
    } finally {
      setLoading(false)
    }
  }

  const removeFavorite = async (advertiserId) => {
    try {
      const response = await fetch(`http://localhost:5000/user/favorites/${advertiserId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        setFavorites(favorites.filter(fav => fav.id !== advertiserId))
      }
    } catch (error) {
      console.error('Erro ao remover favorito:', error)
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

  if (!user) {
    return (
      <Card>
        <CardContent className="text-center py-12">
          <Heart className="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <p className="text-muted-foreground mb-4">
            Faça login para ver seus favoritos
          </p>
          <Button onClick={() => navigate('/login')}>
            Fazer Login
          </Button>
        </CardContent>
      </Card>
    )
  }

  if (loading) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardContent className="p-4">
              <div className="flex items-start gap-4">
                <div className="w-16 h-16 bg-gray-200 rounded"></div>
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                  <div className="h-3 bg-gray-200 rounded w-2/3"></div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  if (favorites.length === 0) {
    return (
      <Card>
        <CardContent className="text-center py-12">
          <Heart className="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <p className="text-muted-foreground mb-2">
            Você ainda não tem favoritos
          </p>
          <p className="text-sm text-muted-foreground mb-4">
            Explore empresas e adicione suas preferidas aos favoritos
          </p>
          <Button onClick={() => navigate('/')}>
            Explorar Empresas
          </Button>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold mb-6">Meus Favoritos</h2>
      
      {favorites.map((advertiser) => (
        <Card key={advertiser.id} className="hover:shadow-md transition-shadow">
          <CardContent className="p-4">
            <div className="flex items-start justify-between">
              <div 
                className="flex-1 cursor-pointer"
                onClick={() => navigate(`/advertiser/${advertiser.id}`)}
              >
                <div className="flex items-start gap-4">
                  {advertiser.logo && (
                    <div className="w-16 h-16 bg-gray-100 rounded-lg flex items-center justify-center">
                      <img 
                        src={advertiser.logo} 
                        alt={advertiser.business_name}
                        className="w-full h-full object-cover rounded-lg"
                      />
                    </div>
                  )}
                  
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <h3 className="font-semibold text-lg">{advertiser.business_name}</h3>
                      <Badge variant="secondary">{advertiser.category}</Badge>
                    </div>
                    
                    <div className="flex items-center gap-2 mb-2 text-sm text-muted-foreground">
                      <MapPin className="w-4 h-4" />
                      <span>{advertiser.city}, {advertiser.state}</span>
                    </div>

                    {advertiser.average_rating > 0 && (
                      <div className="flex items-center gap-2 mb-2">
                        <div className="flex">
                          {renderStars(advertiser.average_rating)}
                        </div>
                        <span className="text-sm text-muted-foreground">
                          ({advertiser.average_rating.toFixed(1)})
                        </span>
                      </div>
                    )}

                    {advertiser.description && (
                      <p className="text-muted-foreground text-sm line-clamp-2">
                        {advertiser.description}
                      </p>
                    )}
                  </div>
                </div>
              </div>

              <Button
                variant="ghost"
                size="sm"
                onClick={() => removeFavorite(advertiser.id)}
                className="text-red-600 hover:text-red-700"
              >
                <Heart className="w-5 h-5 fill-current" />
              </Button>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

export { FavoriteButton, FavoritesList }
export default FavoriteButton

