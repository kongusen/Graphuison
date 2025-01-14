// components/ErrorDisplay.jsx
import React from 'react';
import { Alert } from 'antd';

const ErrorDisplay = ({ message }) => {
    if(!message){
        return null
    }
  return (
    <Alert
      message="Error"
      description={message}
      type="error"
      closable
    />
  );
};

export default ErrorDisplay;