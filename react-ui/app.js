const { useState, useEffect } = React;

function App() {
  const [date, setDate] = useState('');
  const [runId, setRunId] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [schedule, setSchedule] = useState({date:'', frequency:'daily'});

  const startAnalysis = async () => {
    const res = await fetch('/api/analyze?date=' + date, { method: 'POST' });
    const data = await res.json();
    setRunId(data.run_id);
  };

  const loadAnalysis = async () => {
    const res = await fetch('/api/analysis/' + runId);
    const data = await res.json();
    setAnalysis(data);
  };

  const addSchedule = async () => {
    await fetch(`/api/schedule?date=${schedule.date}&frequency=${schedule.frequency}`, {method:'POST'});
    alert('Scheduled!');
  };

  return (
    React.createElement('div', {className:'container'}, [
      React.createElement('h1', {}, 'LLM Chess Coach'),
      React.createElement('div', {}, [
        'Analysis Date: ',
        React.createElement('input', {type:'date', value: date, onChange:e=>setDate(e.target.value)}),
        React.createElement('button', {onClick:startAnalysis}, 'Analyze')
      ]),
      runId && React.createElement('div', {}, [
        React.createElement('p', {}, 'Run ID: '+runId),
        React.createElement('button', {onClick:loadAnalysis}, 'Load Analysis')
      ]),
      analysis && React.createElement('pre', {}, JSON.stringify(analysis, null, 2)),
      React.createElement('h2', {}, 'Schedule Analysis'),
      React.createElement('input', {type:'date', value:schedule.date, onChange:e=>setSchedule({...schedule, date:e.target.value})}),
      React.createElement('select', {value:schedule.frequency, onChange:e=>setSchedule({...schedule, frequency:e.target.value})}, [
        React.createElement('option', {value:'daily'}, 'Daily'),
        React.createElement('option', {value:'weekly'}, 'Weekly')
      ]),
      React.createElement('button', {onClick:addSchedule}, 'Schedule')
    ])
  );
}

ReactDOM.render(React.createElement(App), document.getElementById('root'));
