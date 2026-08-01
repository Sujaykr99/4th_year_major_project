import Sidebar from '../components/layout/Sidebar'
import Topbar from '../components/layout/Topbar'

function DashboardLayout({ activeNav, isSidebarOpen, onToggleSidebar, onChangeNav, onNotice, children }) {
  return (
    <div className={`app-shell ${isSidebarOpen ? 'sidebar-open' : 'sidebar-compact'}`}>
      <Sidebar activeNav={activeNav} isOpen={isSidebarOpen} onToggle={onToggleSidebar} onChangeNav={onChangeNav} onNotice={onNotice} />
      <main className="workspace">
        <Topbar activeNav={activeNav} onChangeNav={onChangeNav} onNotice={onNotice} />
        {children}
      </main>
    </div>
  )
}

export default DashboardLayout
