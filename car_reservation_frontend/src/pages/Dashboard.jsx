import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth.jsx';
import { reservationsAPI, vehiclesAPI } from '@/lib/api';
import { formatDateTime, getStatusColor } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Car, 
  Calendar, 
  Plus, 
  Clock,
  Users,
  Wrench,
  AlertTriangle
} from 'lucide-react';
import './App.css';

const Dashboard = () => {
  const { user, isAdmin } = useAuth();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState({
    myReservations: [],
    vehicles: [],
    stats: {}
  });
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        
        // Fetch user's reservations
        const reservationsResponse = await reservationsAPI.getAll({
          status: 'Confirmed'
        });
        
        // Fetch vehicles
        const vehiclesResponse = await vehiclesAPI.getAll();
        
        // Calculate stats
        const activeVehicles = vehiclesResponse.data.filter(v => v.status === 'Active').length;
        const totalVehicles = vehiclesResponse.data.length;
        const myActiveReservations = reservationsResponse.data.filter(r => 
          r.status === 'Confirmed' && new Date(r.end_time) > new Date()
        ).length;
        
        setData({
          myReservations: reservationsResponse.data.slice(0, 5), // Show only recent 5
          vehicles: vehiclesResponse.data.slice(0, 6), // Show only 6 vehicles
          stats: {
            activeVehicles,
            totalVehicles,
            myActiveReservations,
            totalReservations: reservationsResponse.data.length
          }
        });
        
      } catch (err) {
        setError('Nepodařilo se načíst data dashboardu');
        console.error('Dashboard error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Welcome section */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          Vítejte, {user?.first_name}!
        </h1>
        <p className="text-gray-600">
          Přehled vašich rezervací a dostupných vozidel
        </p>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Car className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Aktivní vozidla</p>
                <p className="text-2xl font-bold text-gray-900">
                  {data.stats.activeVehicles}/{data.stats.totalVehicles}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <Calendar className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Moje aktivní rezervace</p>
                <p className="text-2xl font-bold text-gray-900">
                  {data.stats.myActiveReservations}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {isAdmin() && (
          <>
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-purple-100 rounded-lg">
                    <Users className="h-6 w-6 text-purple-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Celkem rezervací</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {data.stats.totalReservations}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-orange-100 rounded-lg">
                    <Wrench className="h-6 w-6 text-orange-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Správa vozového parku</p>
                    <p className="text-sm text-gray-500">Administrace</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </>
        )}
      </div>

      {/* Quick actions */}
      <Card>
        <CardHeader>
          <CardTitle>Rychlé akce</CardTitle>
          <CardDescription>
            Nejčastěji používané funkce
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-4">
            <Button asChild>
              <Link to="/calendar">
                <Calendar className="mr-2 h-4 w-4" />
                Zobrazit kalendář
              </Link>
            </Button>
            <Button variant="outline" asChild>
              <Link to="/vehicles">
                <Car className="mr-2 h-4 w-4" />
                Prohlédnout vozidla
              </Link>
            </Button>
            <Button variant="outline" asChild>
              <Link to="/my-reservations">
                <Clock className="mr-2 h-4 w-4" />
                Moje rezervace
              </Link>
            </Button>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent reservations */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Moje nedávné rezervace</CardTitle>
                <CardDescription>
                  Posledních 5 rezervací
                </CardDescription>
              </div>
              <Button variant="outline" size="sm" asChild>
                <Link to="/my-reservations">Zobrazit vše</Link>
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {data.myReservations.length === 0 ? (
              <p className="text-gray-500 text-center py-4">
                Nemáte žádné rezervace
              </p>
            ) : (
              <div className="space-y-4">
                {data.myReservations.map((reservation) => (
                  <div key={reservation.reservation_id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div>
                      <p className="font-medium">
                        {reservation.vehicle_info?.make} {reservation.vehicle_info?.model}
                      </p>
                      <p className="text-sm text-gray-600">
                        {reservation.vehicle_info?.license_plate}
                      </p>
                      <p className="text-sm text-gray-500">
                        {formatDateTime(reservation.start_time)} - {formatDateTime(reservation.end_time)}
                      </p>
                    </div>
                    <Badge className={getStatusColor(reservation.status)}>
                      {reservation.status}
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Available vehicles */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Dostupná vozidla</CardTitle>
                <CardDescription>
                  Vozidla připravená k rezervaci
                </CardDescription>
              </div>
              <Button variant="outline" size="sm" asChild>
                <Link to="/vehicles">Zobrazit vše</Link>
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {data.vehicles.filter(v => v.status === 'Active').slice(0, 4).map((vehicle) => (
                <div key={vehicle.vehicle_id} className="p-3 border rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <p className="font-medium">
                      {vehicle.make} {vehicle.model}
                    </p>
                    <Badge className={getStatusColor(vehicle.status)}>
                      {vehicle.status}
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-600 mb-1">
                    {vehicle.license_plate}
                  </p>
                  <p className="text-sm text-gray-500">
                    {vehicle.seating_capacity} míst • {vehicle.fuel_type}
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;

