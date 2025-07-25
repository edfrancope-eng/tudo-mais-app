import { useState, useEffect } from 'react'
import { Star, Send, Flag } from 'lucide-react'
import { Button } from './ui/button'
import { Textarea } from './ui/textarea'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Badge } from './ui/badge'
import { useAuth } from '../contexts/AuthContext'

const ReviewSystem = ({ advertiserId, canReview = false }) => {
  const { user, token } = useAuth()
  const [reviews, setReviews] = useState([])
  const [newReview, setNewReview] = useState({
    rating: 0,
    comment: ''
  })
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [hoveredStar, setHoveredStar] = useState(0)

  useEffect(() => {
    fetchReviews()
  }, [advertiserId])

  const fetchReviews = async () => {
    try {
      const response = await fetch(`http://localhost:5000/advertiser/${advertiserId}/reviews`)
      if (response.ok) {
        const data = await response.json()
        setReviews(data)
      }
    } catch (error) {
      console.error('Erro ao buscar avaliações:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleStarClick = (rating) => {
    setNewReview({ ...newReview, rating })
  }

  const handleStarHover = (rating) => {
    setHoveredStar(rating)
  }

  const handleSubmitReview = async () => {
    if (!newReview.rating || !newReview.comment.trim()) {
      alert('Por favor, selecione uma nota e escreva um comentário.')
      return
    }

    setSubmitting(true)
    try {
      const response = await fetch(`http://localhost:5000/advertiser/${advertiserId}/reviews`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(newReview)
      })

      if (response.ok) {
        setNewReview({ rating: 0, comment: '' })
        fetchReviews() // Recarregar avaliações
        alert('Avaliação enviada com sucesso!')
      } else {
        const data = await response.json()
        alert(data.error || 'Erro ao enviar avaliação')
      }
    } catch (error) {
      console.error('Erro ao enviar avaliação:', error)
      alert('Erro de conexão. Tente novamente.')
    } finally {
      setSubmitting(false)
    }
  }

  const renderStars = (rating, interactive = false, size = 'w-5 h-5') => {
    const stars = []
    const displayRating = interactive ? (hoveredStar || newReview.rating) : rating

    for (let i = 1; i <= 5; i++) {
      stars.push(
        <Star
          key={i}
          className={`${size} cursor-pointer transition-colors ${
            i <= displayRating 
              ? 'fill-yellow-400 text-yellow-400' 
              : 'text-gray-300 hover:text-yellow-400'
          }`}
          onClick={interactive ? () => handleStarClick(i) : undefined}
          onMouseEnter={interactive ? () => handleStarHover(i) : undefined}
          onMouseLeave={interactive ? () => setHoveredStar(0) : undefined}
        />
      )
    }

    return stars
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  const getAverageRating = () => {
    if (reviews.length === 0) return 0
    const sum = reviews.reduce((acc, review) => acc + review.rating, 0)
    return (sum / reviews.length).toFixed(1)
  }

  const getRatingDistribution = () => {
    const distribution = { 5: 0, 4: 0, 3: 0, 2: 0, 1: 0 }
    reviews.forEach(review => {
      distribution[review.rating]++
    })
    return distribution
  }

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="animate-pulse space-y-4">
            <div className="h-4 bg-gray-200 rounded w-1/3"></div>
            <div className="h-20 bg-gray-200 rounded"></div>
            <div className="h-20 bg-gray-200 rounded"></div>
          </div>
        </CardContent>
      </Card>
    )
  }

  const averageRating = getAverageRating()
  const distribution = getRatingDistribution()

  return (
    <div className="space-y-6">
      {/* Resumo das Avaliações */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Avaliações dos Clientes</span>
            <Badge variant="secondary">
              {reviews.length} avaliação{reviews.length !== 1 ? 'ões' : ''}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {reviews.length > 0 ? (
            <div className="space-y-4">
              <div className="flex items-center gap-4">
                <div className="text-center">
                  <div className="text-3xl font-bold">{averageRating}</div>
                  <div className="flex justify-center">
                    {renderStars(parseFloat(averageRating))}
                  </div>
                  <div className="text-sm text-muted-foreground mt-1">
                    Média geral
                  </div>
                </div>

                <div className="flex-1 space-y-2">
                  {[5, 4, 3, 2, 1].map(rating => (
                    <div key={rating} className="flex items-center gap-2 text-sm">
                      <span className="w-3">{rating}</span>
                      <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                      <div className="flex-1 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-yellow-400 h-2 rounded-full"
                          style={{ 
                            width: `${reviews.length > 0 ? (distribution[rating] / reviews.length) * 100 : 0}%` 
                          }}
                        ></div>
                      </div>
                      <span className="w-8 text-right">{distribution[rating]}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <Star className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <p>Ainda não há avaliações para esta empresa.</p>
              <p className="text-sm">Seja o primeiro a avaliar!</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Formulário de Nova Avaliação */}
      {canReview && user && (
        <Card>
          <CardHeader>
            <CardTitle>Deixe sua Avaliação</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                Sua nota:
              </label>
              <div className="flex gap-1">
                {renderStars(newReview.rating, true, 'w-8 h-8')}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Seu comentário:
              </label>
              <Textarea
                placeholder="Conte sobre sua experiência com esta empresa..."
                value={newReview.comment}
                onChange={(e) => setNewReview({ ...newReview, comment: e.target.value })}
                rows={4}
                maxLength={500}
              />
              <div className="text-xs text-muted-foreground mt-1">
                {newReview.comment.length}/500 caracteres
              </div>
            </div>

            <Button
              onClick={handleSubmitReview}
              disabled={submitting || !newReview.rating || !newReview.comment.trim()}
              className="bg-green-600 hover:bg-green-700"
            >
              {submitting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Enviando...
                </>
              ) : (
                <>
                  <Send className="w-4 h-4 mr-2" />
                  Enviar Avaliação
                </>
              )}
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Lista de Avaliações */}
      {reviews.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Comentários dos Clientes</h3>
          
          {reviews.map((review) => (
            <Card key={review.id}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-medium">{review.user_name || 'Cliente'}</span>
                      <div className="flex">
                        {renderStars(review.rating, false, 'w-4 h-4')}
                      </div>
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {formatDate(review.created_at)}
                    </div>
                  </div>
                  
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-red-600 hover:text-red-700"
                    onClick={() => {
                      // TODO: Implementar denúncia de comentário
                      alert('Comentário denunciado. Será analisado pela moderação.')
                    }}
                  >
                    <Flag className="w-4 h-4" />
                  </Button>
                </div>
                
                <p className="text-muted-foreground leading-relaxed">
                  {review.comment}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}

export default ReviewSystem

