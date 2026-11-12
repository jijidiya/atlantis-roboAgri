import StatCard from '../components/StatCard'
import StatusBadge from '../components/StatusBadge'
import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, ReferenceLine,
} from 'recharts'
import { activite, humidite, comparaison } from '../data/rapports'

function Rapports() {
  const totalMissions = activite.reduce((s, j) => s + j.terminees + j.autres, 0)
  const totalTerminees = activite.reduce((s, j) => s + j.terminees, 0)
  const taux = Math.round((totalTerminees / totalMissions) * 100)

  const derniere = humidite[humidite.length - 1]
  const moyenne = ((derniere.A + derniere.B + derniere.C) / 3).toFixed(1)

  const totalRecos = comparaison.reduce((s, z) => s + z.recommandations, 0)

  return (
    <div>
      <div className="titre-ligne">
        <div>
          <h1>Rapports et statistiques</h1>
          <p className="sous-titre">Transformez les données du terrain en décisions éclairées.</p>
        </div>
        <button className="bouton-principal" onClick={() => window.print()}>Générer un rapport</button>
      </div>

      <div className="cartes">
        <StatCard titre="Missions de la semaine" valeur={String(totalMissions)} details="7 derniers jours" />
        <StatCard titre="Taux d’achèvement" valeur={`${taux} %`} details={`${totalTerminees} missions terminées sur ${totalMissions}`} />
        <StatCard titre="Humidité moyenne" valeur={`${moyenne} %`} details="Dernière mesure · 3 zones" />
        <StatCard titre="Recommandations d’arrosage" valeur={String(totalRecos)} details="Sur 7 jours" />
      </div>

      <div className="rangee-graphiques">
        <div className="carte-mission">
          <strong>Activité des missions</strong>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={activite}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="jour" />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Legend />
              <Bar dataKey="terminees" name="Terminées" stackId="a" fill="#166534" />
              <Bar dataKey="autres" name="Autres statuts" stackId="a" fill="#d6a85c" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="carte-mission">
          <strong>Humidité par zone</strong>
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={humidite}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="heure" />
              <YAxis domain={[0, 70]} unit=" %" />
              <Tooltip />
              <Legend />
              <ReferenceLine y={30} stroke="#c2410c" strokeDasharray="5 5" label="Seuil bas" />
              <Line type="monotone" dataKey="A" name="Zone A" stroke="#166534" dot={false} />
              <Line type="monotone" dataKey="B" name="Zone B" stroke="#b45309" dot={false} />
              <Line type="monotone" dataKey="C" name="Zone C" stroke="#6aa583" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <h2>Comparaison des zones</h2>
      <table className="tableau">
        <thead>
          <tr><th>Zone / Culture</th><th>Humidité</th><th>Recommandations · 7 j</th><th>Missions</th><th>État</th></tr>
        </thead>
        <tbody>
          {comparaison.map((z) => (
            <tr key={z.zone}>
              <td>{z.zone}</td>
              <td>{z.humidite} %</td>
              <td>{z.recommandations}</td>
              <td>{z.missions}</td>
              <td><StatusBadge statut={z.etat} /></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default Rapports