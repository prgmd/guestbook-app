import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [entries, setEntries] = useState([]);
  const [name, setName] = useState('');
  const [content, setContent] = useState('');

  const QUERY_API_URL = '/api/query/entries';
  const COMMAND_API_URL = '/api/command/entries';

  useEffect(() => {
    fetchEntries();
  }, []);

  const fetchEntries = async () => {
    try {
      const response = await fetch(QUERY_API_URL);
      const data = await response.json();
      setEntries(data);
    } catch (error) {
      console.error("Error fetching entries:", error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name.trim() || !content.trim()) {
      alert("이름과 내용을 모두 입력해주세요.");
      return;
    }
    try {
      const response = await fetch(COMMAND_API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, content }),
      });
      if (response.ok) {
        setName('');
        setContent('');
        setTimeout(() => fetchEntries(), 500);
      } else {
        alert("등록에 실패했습니다.");
      }
    } catch (error) {
      console.error("Error creating entry:", error);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("정말로 이 글을 삭제하시겠습니까?")) return;
    try {
      const response = await fetch(`${COMMAND_API_URL}/${id}`, {
        method: 'DELETE',
      });
      if (response.ok) {
        setTimeout(() => fetchEntries(), 500);
      } else {
        alert("삭제에 실패했습니다.");
      }
    } catch (error) {
      console.error("Error deleting entry:", error);
    }
  };

  return (
    <div className="app-container">      
      <div className="guestbook-window">
        {/* 창 상단의 타이틀 바 */}
        <div className="title-bar">
          <div className="window-controls">
            <span className="control-btn close"></span>
            <span className="control-btn minimize"></span>
            <span className="control-btn maximize"></span>
          </div>
          <span className="title-text">GUESTBOOK</span>
        </div>

        {/* 실제 내용이 들어가는 영역 */}
        <div className="window-content">
          {/* 글 작성 폼 */}
          <form onSubmit={handleSubmit} className="guestbook-form">
            <input
              type="text"
              className="input-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="이름"
              required
            />
            <textarea
              className="input-content"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="내용을 입력하세요."
              required
            ></textarea>
            <button type="submit" className="submit-btn">등록하기</button>
          </form>

          <hr className="divider" />

          {/* 방명록 목록 */}
          <div className="guestbook-entries">
            {entries.length > 0 ? (
              entries.map((entry) => (
                <div key={entry.id} className="entry">
                  <div className="entry-header">
                    <strong className="entry-author">{entry.name}</strong>
                    {/* 시간과 삭제 버튼을 함께 묶는 .entry-meta div를 추가합니다. */}
                    <div className="entry-meta">
                      <span className="entry-timestamp">{entry.created_at}</span>
                      <button onClick={() => handleDelete(entry.id)} className="delete-btn">
                        삭제
                      </button>
                    </div>
                  </div>
                  <p className="entry-body">{entry.content}</p>
                </div>
              ))
            ) : (
              <p className="no-entries-msg">등록된 글이 없습니다.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;