// components/LoadingIndicator.jsx
import React from 'react';
import { Spin } from 'antd';

const LoadingIndicator = () => {
return (
  <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100px' }}>
    <Spin size="large" />
  </div>
 );
};

export default LoadingIndicator;