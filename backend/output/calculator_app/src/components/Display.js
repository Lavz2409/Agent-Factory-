javascript
import React from 'react';
import styled from 'styled-components';

const DisplayContainer = styled.div`
  background-color: #282c34;
  color: white;
  font-size: 2em;
  padding: 20px;
  text-align: right;
  border-radius: 5px;
  margin-bottom: 20px;
`;

const Display = ({ input, result }) => {
  return (
    <DisplayContainer>
      <div>{input}</div>
      <div>{result}</div>
    </DisplayContainer>
  );
};

export default Display;