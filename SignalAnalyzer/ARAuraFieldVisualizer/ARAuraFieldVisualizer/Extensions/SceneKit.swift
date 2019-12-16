//
//  SceneKit.swift
//  ARAuraFieldVisualizer
//
//  Created by Jordan Trana on 11/10/19.
//  Copyright © 2019 Jordan Trana. All rights reserved.
//

import SceneKit


extension SCNVector3 {
    func length() -> CGFloat {
        return CGFloat(sqrtf(x * x + y * y + z * z))
    }
    
    func distance(between otherVector:SCNVector3) -> CGFloat {
        let diff = self - otherVector
        return diff.length()
    }
}
func - (l: SCNVector3, r: SCNVector3) -> SCNVector3 {
    return SCNVector3Make(l.x - r.x, l.y - r.y, l.z - r.z)
}
func + (l: SCNVector3, r: SCNVector3) -> SCNVector3 {
    return SCNVector3Make(l.x + r.x, l.y + r.y, l.z + r.z)
}


extension SCNNode {
    
    func printContents() {
        print(allChildStrings())
    }
    
    func allChildStrings() -> [String] {
        var list:[String] = []
        for childNode in childNodes {
            
            list.append(String(describing: childNode))
            
            for subChildNodeString in childNode.allChildStrings() {
                list.append("\(String(describing: childNode)): \(subChildNodeString)")
            }
        }
        return list
    }
}
