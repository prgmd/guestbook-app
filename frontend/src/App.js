import React, { useState, useEffect } from 'react';
import './App.css'; // 간단한 스타일링을 위해 추가

function App() {
  const [entries, setEntries] = useState([]);
  const [name, setName] = useState('');
  const [content, setContent] = useState('');

  // 백엔드 API 주소 (docker-compose 환경 기준)
  // Nginx 프록시를 사용할 것이므로 상대 경로로 지정합니다.
  const QUERY_API_URL = '/api/query/entries';
  const COMMAND_API_URL = '/api/command/entries';

  // 글 목록 조회 (GET)
  const fetchEntries = async () => {
    try {
      const response = await fetch(QUERY_API_URL); // <-- URL 변경
      const data = await response.json();
      setEntries(data);
    } catch (error) {
      console.error("Error fetching entries:", error);
    }
  };

  // 글 작성 (POST)
  const handleSubmit = async (e) => {
    e.preventDefault();
    // ... (유효성 검사)
    try {
      const response = await fetch(COMMAND_API_URL, { // <-- URL 변경
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, content }),
      });
      if (response.ok) {
        setName('');
        setContent('');
        // 글 작성 후 바로 목록을 다시 불러오지 않고,
        // eventual consistency를 위해 약간의 딜레이를 주거나
        // 사용자에게 잠시 후 반영된다는 메시지를 보여주는 것이 좋음
        setTimeout(() => fetchEntries(), 500); // 0.5초 후 목록 새로고침
      } else {
        alert("등록에 실패했습니다.");
      }
    } catch (error) { /* ... */ }
  };

  // 글 삭제 (DELETE)
  const handleDelete = async (id) => {
    if (!window.confirm("정말로 이 글을 삭제하시겠습니까?")) return;
    try {
      const response = await fetch(`${COMMAND_API_URL}/${id}`, { // <-- URL 변경
        method: 'DELETE',
      });
      if (response.ok) {
        // 성공 시 낙관적 업데이트(Optimistic Update) 또는 목록 새로고침
        fetchEntries();
      } else {
        alert("삭제에 실패했습니다.");
      }
    } catch (error) { /* ... */ }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>방명록</h1>
        <form onSubmit={handleSubmit} className="guestbook-form">
          <div className="form-group">
            <label htmlFor="name">이름</label>
            <input
              type="text"
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="이름을 입력하세요"
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="content">내용</label>
            <textarea
              id="content"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="내용을 입력하세요"
              required
            ></textarea>
          </div>
          <button type="submit">등록하기</button>
        </form>

        <div className="guestbook-entries">
          <h2>글 목록</h2>
          {entries.length > 0 ? (
            entries.map((entry) => (
              <div key={entry.id} className="entry">
                <div className="entry-header">
                  <strong>{entry.name}</strong>
                  <div className="entry-meta">
                    <span>{entry.created_at}</span>
                    <button onClick={() => handleDelete(entry.id)} className="delete-btn">
                      삭제
                    </button>
                  </div>
                </div>
                <p>{entry.content}</p>
              </div>
            ))
          ) : (
            <p>아직 등록된 글이 없습니다.</p>
          )}
        </div>
      </header>
    </div>
  );
}

export default App;