function Toggle({ actif, onChange }) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={actif}
      className={actif ? 'toggle on' : 'toggle'}
      onClick={() => onChange(!actif)}
    >
      <span />
    </button>
  )
}

export default Toggle