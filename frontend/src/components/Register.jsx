import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Label } from './ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select'
import { Textarea } from './ui/textarea'
import { Checkbox } from './ui/checkbox'
import { Alert, AlertDescription } from './ui/alert'

const Register = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    birth_date: '',
    cpf: '',
    business_name: '',
    description: '',
    phone: '',
    website: '',
    address: '',
    city_id: '',
    category_id: '',
    ad_scope: 'CITY'
  })
  const [acceptTerms, setAcceptTerms] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  
  const navigate = useNavigate()

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSelectChange = (name, value) => {
    setFormData({
      ...formData,
      [name]: value
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (!acceptTerms) {
      setError('Você deve aceitar os termos de uso')
      return
    }

    setLoading(true)

    try {
      const response = await fetch('https://tudo-mais-app-production.up.railway.app/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...formData,
          city_id: parseInt(formData.city_id) || 1, // Valor padrão temporário
          category_id: parseInt(formData.category_id) || 1 // Valor padrão temporário
        })
      })

      const data = await response.json()

      if (response.ok) {
        alert('Cadastro realizado com sucesso! Período de teste de 7 dias iniciado.')
        navigate('/login')
      } else {
        setError(data.error || 'Erro ao realizar cadastro')
      }
    } catch (error) {
      setError('Erro de conexão. Tente novamente.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-2xl mx-auto">
        <Card>
          <CardHeader className="text-center">
            <CardTitle className="text-2xl">
              Cadastre sua empresa no <span className="tudo-mais-green">Tudo Mais</span>
            </CardTitle>
            <p className="text-muted-foreground">
              7 dias grátis para testar todas as funcionalidades
            </p>
          </CardHeader>
          <CardContent>
            {error && (
              <Alert className="mb-4 border-red-200 bg-red-50">
                <AlertDescription className="text-red-800">
                  {error}
                </AlertDescription>
              </Alert>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Dados Pessoais */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Dados Pessoais</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="name">Nome Completo *</Label>
                    <Input
                      id="name"
                      name="name"
                      value={formData.name}
                      onChange={handleChange}
                      required
                      placeholder="Seu nome completo"
                    />
                  </div>

                  <div>
                    <Label htmlFor="birth_date">Data de Nascimento *</Label>
                    <Input
                      id="birth_date"
                      name="birth_date"
                      type="date"
                      value={formData.birth_date}
                      onChange={handleChange}
                      required
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="cpf">CPF *</Label>
                    <Input
                      id="cpf"
                      name="cpf"
                      value={formData.cpf}
                      onChange={handleChange}
                      required
                      placeholder="000.000.000-00"
                    />
                  </div>

                  <div>
                    <Label htmlFor="email">Email *</Label>
                    <Input
                      id="email"
                      name="email"
                      type="email"
                      value={formData.email}
                      onChange={handleChange}
                      required
                      placeholder="seu@email.com"
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="password">Senha *</Label>
                  <Input
                    id="password"
                    name="password"
                    type="password"
                    value={formData.password}
                    onChange={handleChange}
                    required
                    placeholder="Crie uma senha segura"
                  />
                </div>
              </div>

              {/* Dados da Empresa */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Dados da Empresa</h3>
                
                <div>
                  <Label htmlFor="business_name">Nome da Empresa *</Label>
                  <Input
                    id="business_name"
                    name="business_name"
                    value={formData.business_name}
                    onChange={handleChange}
                    required
                    placeholder="Nome da sua empresa"
                  />
                </div>

                <div>
                  <Label htmlFor="description">Descrição da Empresa</Label>
                  <Textarea
                    id="description"
                    name="description"
                    value={formData.description}
                    onChange={handleChange}
                    placeholder="Descreva sua empresa e seus serviços"
                    rows={3}
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="phone">Telefone *</Label>
                    <Input
                      id="phone"
                      name="phone"
                      value={formData.phone}
                      onChange={handleChange}
                      required
                      placeholder="(11) 99999-9999"
                    />
                  </div>

                  <div>
                    <Label htmlFor="website">Site (opcional)</Label>
                    <Input
                      id="website"
                      name="website"
                      value={formData.website}
                      onChange={handleChange}
                      placeholder="https://seusite.com"
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="address">Endereço</Label>
                  <Input
                    id="address"
                    name="address"
                    value={formData.address}
                    onChange={handleChange}
                    placeholder="Rua, número, bairro"
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label>Categoria *</Label>
                    <Select onValueChange={(value) => handleSelectChange('category_id', value)}>
                      <SelectTrigger>
                        <SelectValue placeholder="Selecione uma categoria" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="1">Alimentação</SelectItem>
                        <SelectItem value="2">Saúde</SelectItem>
                        <SelectItem value="3">Educação</SelectItem>
                        <SelectItem value="4">Tecnologia</SelectItem>
                        <SelectItem value="5">Serviços</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label>Cidade *</Label>
                    <Select onValueChange={(value) => handleSelectChange('city_id', value)}>
                      <SelectTrigger>
                        <SelectValue placeholder="Selecione sua cidade" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="1">São Paulo - SP</SelectItem>
                        <SelectItem value="2">Rio de Janeiro - RJ</SelectItem>
                        <SelectItem value="3">Belo Horizonte - MG</SelectItem>
                        <SelectItem value="4">Salvador - BA</SelectItem>
                        <SelectItem value="5">Brasília - DF</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div>
                  <Label>Anunciar em:</Label>
                  <Select onValueChange={(value) => handleSelectChange('ad_scope', value)} defaultValue="CITY">
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="CITY">Minha Cidade</SelectItem>
                      <SelectItem value="CITY_REGION">Minha Cidade e Região</SelectItem>
                      <SelectItem value="CITY_REGION_OTHER_STATES">Minha Cidade, Região e Outros Estados</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {/* Termos */}
              <div className="flex items-center space-x-2">
                <Checkbox 
                  id="terms" 
                  checked={acceptTerms}
                  onCheckedChange={setAcceptTerms}
                />
                <Label htmlFor="terms" className="text-sm">
                  Aceito os termos de uso e política de privacidade. Confirmo que sou maior de 18 anos e que as informações fornecidas são verdadeiras.
                </Label>
              </div>

              <Button 
                type="submit" 
                className="w-full bg-tudo-mais-green hover:bg-tudo-mais-dark-green"
                disabled={loading}
              >
                {loading ? 'Cadastrando...' : 'Cadastrar Empresa'}
              </Button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-sm text-muted-foreground">
                Já tem uma conta?{' '}
                <Link to="/login" className="tudo-mais-green hover:underline">
                  Fazer login
                </Link>
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default Register

