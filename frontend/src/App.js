import React, { useState, useEffect } from 'react';
import './App.css'; // 간단한 스타일링을 위해 추가

function App() {
  const [entries, setEntries] = useState([]);
  const [name, setName] = useState('');
  const [content, setContent] = useState('');

  // 백엔드 API 주소 (docker-compose 환경 기준)
  // Nginx 프록시를 사용할 것이므로 상대 경로로 지정합니다.
  const API_URL = '/api/entries';

  // 컴포넌트가 처음 렌더링될 때 방명록 목록을 불러옵니다.
  useEffect(() => {
    fetchEntries();
  }, []);

  // 방명록 목록을 서버에서 가져오는 함수
  const fetchEntries = async () => {
    try {
      const response = await fetch(API_URL);
      const data = await response.json();
      setEntries(data);
    } catch (error) {
      console.error("Error fetching entries:", error);
    }
  };

  // 폼 제출 처리 함수
  const handleSubmit = async (e) => {
    e.preventDefault(); // 폼 기본 제출 동작 방지

    if (!name.trim() || !content.trim()) {
      alert("이름과 내용을 모두 입력해주세요.");
      return;
    }

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, content }),
      });

      if (response.ok) {
        // 성공적으로 등록되면 입력 필드를 비우고 목록을 새로고침합니다.
        setName('');
        setContent('');
        fetchEntries(); // 목록 다시 불러오기
      } else {
        alert("등록에 실패했습니다.");
      }
    } catch (error) {
      console.error("Error creating entry:", error);
    }
  };

  // 삭제 처리 함수
  const handleDelete = async (id) => {
    // 사용자에게 삭제 여부를 한 번 더 확인받습니다.
    if (!window.confirm("정말로 이 글을 삭제하시겠습니까?")) {
      return;
    }

    try {
      const response = await fetch(`${API_URL}/${id}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        // 성공적으로 삭제되면, 화면에서도 해당 글을 즉시 제거합니다.
        // 서버에서 목록을 다시 불러오는 대신, 상태를 직접 업데이트하여 더 빠른 반응성을 제공합니다.
        setEntries(entries.filter(entry => entry.id !== id));
      } else {
        alert("삭제에 실패했습니다.");
      }
    } catch (error) {
      console.error("Error deleting entry:", error);
    }
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