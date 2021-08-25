import React, { useState } from 'react'

function App() {
  const [count, setCount] = useState(0)
  // https://api.github.com/users

  return (
    <>
      <nav className="bg-[#4fc677] py-2 px-8">
        <a href="https://simplesat.io">
          <img
            style={{
              height: 40,
            }}
            src="https://cdn.simplesat.io/images/simplesat-logomark-white-large.png?size=40"
            alt="Simplesat logo"
          />
        </a>
      </nav>
      <div className="container mx-auto p-8">
        <h1>GitHub users</h1>
        <ul>
          <li>
            <h2>{'<Username>'}</h2>
            <p>ID: {'<id>'}</p>
          </li>
        </ul>
      </div>
    </>
  )
}

export default App
